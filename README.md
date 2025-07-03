# pyvrp_docker 🚚

A Dockerized setup for running [PyVRP](https://github.com/PyVRP/PyVRP) — a high-performance solver for Vehicle Routing Problems — combined with a multiprocessing system for efficiently launching and managing large-scale experiments.

---

## 🔍 What is PyVRP?

[PyVRP](https://github.com/PyVRP/PyVRP) is a hybrid C++/Python library implementing state-of-the-art heuristics for different VRP types:

This container allows you to run PyVRP CVRPs with your own distance matrices in parallel with preconfigured demand scenarios based on the X-Sets (https://www.sciencedirect.com/science/article/abs/pii/S0377221716306270) 

Use the debug.vrp file in data/Vrp-Set-X/X/debug.vrp for custom demand scenarios
---

### ⚙️Prerequisites

- pip/python
- pip install -r requirements.txt
- gcloud cli for remote deployment
- Custom distance matrices in json format like data/distance_matrices/Chicago_100x100_RoadData.json

### Local Deployment
- The flask_endpoint.py launches a webserver with exposed ports --> Not recommended on local pc
- Can be adapted in the build_upload.sh and flask_endpoint.py for different behavior


### Build and Launch (Linux)

Normal GCP c4a-highcpu-8 launch (any c4a instance will dow)

Requires: gcloud-cli with running vm instance (can be started in 4core/8core version using 4coreStart.sh or 8coreStart.sh)

```bash
# Clone the repository
git clone https://github.com/zrtgzrtg/pyvrp_docker.git
cd pyvrp_docker

# Build Docker image
chmod +x build_upload.sh
./build_upload.sh

# SSH into GCP VM
gcloud compute ssh chosen-VM-Name --zone=chosen-VM-zone
```

# Importing distance matrices

- Put distance matrices into data/distance_matrices and add entry into data/city_matrices.py
- This expects a pair of distance_matrices as the main objective of this project is the comparison between euclidean and real road network routing decisions
- Put the same filepath into data/city_matrices.py for just one DM solve

# Sampling

- Sampler.py provides utilities for random Sampling of large distance matrices
- Configure filepaths in the code for the naming of specific distance matrix
- If Sample3DMs is used the output is a directory filled with DMs as sub-matrices from original
- Use BatchQueue.py createRunningFile() to create runFile for this dir
- change main method in BatchQueue.py to runRunningFile(filename) and start through POST Request on webserver
- copy BatchCustom or BatchDir after finished run for the results

# Swapping

- Swap specific IDs of 2 distance matrices by using the Swapper.py class
- Mostly done to create hybrid distance matrices from a real road network DM and a euclidean DM


