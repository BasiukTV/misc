**Script for simulating effects of cache co-location for multiple tenants.**

## Dependencies
- Python3
- `> pip install cachetools`
- `> pip install matplotlib`

## Usage Examples

`$ python cache_cl_sim.py --help`

`$ python cache_cl_sim.py 10 1 1 1 1 1 1 1 1 1 0.5`

```
$ python cache_cl_sim.py 10 1 1 1 1 1 1 1 1 1 1 `
    --min-tenant-calls 1000 `
    --tenant-cache-key-space 100 100 100 100 100 100 100 100 100 500 `
    --tenant-cache-capacity 80 80 80 80 80 80 80 80 80 400 `
    --metric-recording-period 50
```

## Result Examples
[[https://github.com/BasiukTV/misc/sim/cache/example/example1.png|alt=octocat]]
[[https://github.com/BasiukTV/misc/sim/cache/example/example2.png|alt=octocat]]
