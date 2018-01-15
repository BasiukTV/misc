import argparse, cachetools, itertools, matplotlib.pyplot as plt, random

# Global counter for designated tenant cache misses for every tennant. Has to be reset for every tenant.
designated_cache_miss_counter = 0

# Global counter for co-located cache misses corresponding to a particular tenant
colocated_cache_miss_counter = {}

'''
    Prefix multiplier used to distinguish particular tenant among diferent cache keys
    For example, when prefix multiplier is 100, cache key "213" corresponds to tenant #2 and item #13
'''
tenant_index_prefix_multiplier = 10

# Function called on a designated tenant cache miss
def designated_cache_miss(cache_key):
    global designated_cache_miss_counter

    designated_cache_miss_counter += 1 # Increment 
    return True # We don't care about actual items stored in cache, so simply return True 

# Function called on co-located cache miss
def colocated_cache_miss(cache_key):
    global colocated_cache_miss_counter

    # Decode tenant index from cache key and record cache miss for that tenant
    colocated_cache_miss_counter[cache_key // tenant_index_prefix_multiplier] += 1
    return True # We don't care about actual items stored in cache, so simply return True 

# Function for running co-located cache simulation and collecting cache misses for all the tenants involved
def run_simulation(tenants, call_rates, min_calls, key_space_sizes, cache_capacities, metrics_recording_period):
    global designated_cache_miss_counter, colocated_cache_miss_counter, tenant_index_prefix_multiplier

    print("Starting simulation.")

    # If key_space_sizes only contains one element, make number of copies of it equal to number of tenants
    if tenants != 1 and len(key_space_sizes) == 1:
        key_space_sizes = key_space_sizes * tenants

    # If cache_capacities only contains one element, make number of copies of it equal to number of tenants
    if tenants != 1 and len(cache_capacities) == 1:
        cache_capacities = cache_capacities * tenants

    # Adjust all call rates so the smallest call rate is 1
    call_rate_normalizer = min(call_rates)
    adjusted_call_rates = []
    for i in range(tenants):
        adjusted_call_rates.append(call_rates[i] / call_rate_normalizer)
    print("\tNormalized tenant call rates: {}".format(adjusted_call_rates))

    # Calculate number of cache calls every tenant will receive
    calls_per_tennant = []
    for i in range(tenants):
        calls_per_tennant.append(int(adjusted_call_rates[i] * min_calls))
    print("\tEach tenant's cache will receive {} calls.".format(calls_per_tennant))

    # Determining the value of tenant_index_prefix_multiplier sufficient for errorless encoding of tenant indexes into cache keys
    max_key_val = max(key_space_sizes)
    while tenant_index_prefix_multiplier <= max_key_val:
        tenant_index_prefix_multiplier *= 10

    print("Generating cache calls using uniformal distribution of tenant-disjoint cache keys.")
    cache_calls = [] # Container for cache calls for all tenants
    for i in range(tenants):
        cache_calls.append([]) # Initialize a list for cache calls for tenant i

        # Initialize designated cache
        designated_tenant_cache = cachetools.LRUCache(maxsize=cache_capacities[i], missing=designated_cache_miss)
        designated_cache_miss_counter = 0 # Initialize designated cache miss counter
        colocated_cache_miss_counter[i + 1] = 0 # Initialize miss counter for tenant i in co-located cache

        for _ in range(calls_per_tennant[i]):
            cache_key = (i + 1) * tenant_index_prefix_multiplier + random.randrange(key_space_sizes[i]) # Generate cache key with tenant index encoded
            cache_calls[i].append(cache_key) # Store generated key

            # Retrieve a cache item from designated cache and do nothing with it, we only care about recording miss rates
            designated_tenant_cache[cache_key]

        print("\tRunning standalone, LRU cache of tenant #{} of size {} would generate approximately {:.2f}% of cache misses."
            .format(i + 1, cache_capacities[i], 100 * designated_cache_miss_counter / calls_per_tennant[i]))

    print("\tNote! Above cache miss estimations contain 'cold' cache misses.")

    print("Initializing co-located LRU cache of size {} and collecting cache miss metrics for every tenant.".format(sum(cache_capacities)))
    colocated_cache = cachetools.LRUCache(maxsize=sum(cache_capacities), missing=colocated_cache_miss)

    shuffled_cache_calls = list(itertools.chain.from_iterable(cache_calls)) # Join cache calls of all tenants
    random.shuffle(shuffled_cache_calls) # Shuffle all cache calls

    # Initialize the metrics
    colocated_cache_hit_rate_data = {} # Container for cache hit metrics for every tenant
    colocated_cache_call_counters = {} # Container for cache call metrics for every tenant
    metrics_recording_time = [0] # Container for recording when (after how many cache calls) miss metrics were recorded
    for i in range(1, tenants + 1):
        colocated_cache_hit_rate_data[i] = [0] # We set initial cache hit value to zero
        colocated_cache_call_counters[i] = 0

    # Run co-locates cache calls simulation
    for i in range(1, len(shuffled_cache_calls) + 1):
        # Retrieve a cache item from co-located cache and do nothing with it, we only care about recording miss rates
        colocated_cache[shuffled_cache_calls[i - 1]]

        # Decode tenant index, for which cache call was made and increment corresponding counter
        tenant_index = shuffled_cache_calls[i - 1] // tenant_index_prefix_multiplier
        colocated_cache_call_counters[tenant_index] += 1

        # If it's time to record miss metrics, do so
        if i % metrics_recording_period == 0 or i == len(shuffled_cache_calls):
            metrics_recording_time.append(i)
            for j in range(1, tenants + 1):
                colocated_cache_hit_rate_data[j].append(0 if colocated_cache_call_counters[j] == 0 else 100 * (1 - (colocated_cache_miss_counter[j] / colocated_cache_call_counters[j])))

    print("Visualizing the results of the simulation.")
    plt.figure(figsize=(10, 6))
    ax = plt.subplot(111)
    for i in range(1, tenants + 1):
        plt.plot(metrics_recording_time, colocated_cache_hit_rate_data[i],
            label="#{} Call Rate: {}, Key Space Size: {}".format(i, call_rates[i - 1], key_space_sizes[i - 1]))

    plt.title('Simulating Cache Co-Location of Multiple Tenants\nType: {}, Size: {}, Key Distribution: {}'.format("LRU", sum(cache_capacities), "Uniformal"))
    plt.xlabel('Cache Calls Made')
    plt.ylabel('Per Tenant Cache Hit % Over Last {} Calls'.format("ALL"))
    ax.set_yticks(list(range(0, 110, 10)))
    ax.grid(True, axis="y", linestyle='dotted')
    plt.legend(loc='upper right')
    plt.show()

if __name__ == "__main__":

    # Configuring CLI arguments parser and parsing the arguments
    parser = argparse.ArgumentParser("Script for simulating effects of cache co-location for multiple tenants.")

    # Required/Positional Parameters
    parser.add_argument("TENANTS", type=int, help="Number of tenants to use for co-location. Has to be a positive integer.")
    parser.add_argument("CALL_RATES", type=float, nargs="+", help="Relative tenant cache call rates. One positive float for each tenant is expected.")

    # Optional Parameters
    parser.add_argument("-mtc", "--min-tenant-calls", type=int, default=10000, help="Minimal number of calls any tenant's cache will receive. Must be at least 10.")
    parser.add_argument("-tcks", "--tenant-cache-key-space", type=int, nargs="+", default=[100], help="Key space size of each tenant. Positive integer expected. One for all tenants, or a list for each one.")
    parser.add_argument("-tcc", "--tenant-cache-capacity", type=int, nargs="+", default=[80], help="Cache capacity of each tenant (before co-location). Positive integer expected. One for all tenants, or a list for each one.")
    parser.add_argument("-mrd", "--metric-recording-period", type=int, default=100, help="Number of calls to co-located cache after which hit metrics will be recorded.")

    args = parser.parse_args()

    # Additional input parameters validation activities
    if (args.TENANTS < 1):
        print("ERROR! Simulation can only be done for at least one tenant. Given: {}".format(args.TENANTS))
        exit()

    if (len(args.CALL_RATES) != args.TENANTS or min(args.CALL_RATES) <= 0):
        print("ERROR! Expected {} call rates provided, each a positive float. Given: {}".format(args.TENANTS, args.CALL_RATES))
        exit()

    if (args.min_tenant_calls < 10):
        print("ERROR! Minimal number of calls to any tenants cache must be at least 10. Given: {}".format(args.min_tenant_calls))
        exit()

    if ((len(args.tenant_cache_key_space) != 1 and len(args.tenant_cache_key_space) != args.TENANTS) or min(args.tenant_cache_key_space) < 1):
        print("ERROR! Expected one positive tenant cache key size provided, or a list of one for each of {} tenants. Given: {}".format(args.TENANTS, args.tenant_cache_key_space))
        exit()

    if ((len(args.tenant_cache_capacity) != 1 and len(args.tenant_cache_capacity) != args.TENANTS) or min(args.tenant_cache_capacity) < 1):
        print("ERROR! Expected one positive tenant cache capcity provided, or a list of one for each of {} tenants. Given: {}".format(args.TENANTS, args.tenant_cache_capacity))
        exit()

    if (args.metric_recording_period < 1):
        print("ERROR! Metric recording period must be positive. Given: {}".format(args.metric_recording_period))
        exit()

    # Print out results of input arguments parsing back to the user
    print("Will run the simulation with the following parameters:")
    print("\tNumber of tenants to co-locate: {}".format(args.TENANTS))
    print("\tRelative tenant cache call rates: {}".format(args.CALL_RATES))
    print("\tEach tenant's cache will receive at least {} calls.".format(args.min_tenant_calls))
    print("\tTenant cache key space sizes: {}".format(args.tenant_cache_key_space))
    print("\tTenant standalone cache capacities: {}".format(args.tenant_cache_capacity))
    print("\tWill record co-located cache miss metrics over every {} calls.".format(args.metric_recording_period))

    run_simulation(args.TENANTS, args.CALL_RATES, args.min_tenant_calls, args.tenant_cache_key_space, args.tenant_cache_capacity, args.metric_recording_period)
    print("All Done.")
