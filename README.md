# WOKO New Room Notifier

_Python script sending push notifications whenever a new room is published on the WOKO (student association for housing in Zurich) website or on wgzimmer._

<p align="center">
  <img src="notification_sample.jpg" width="450" title="Sample Notifications">
</p>

## What this Script Does

This script continuously fetches the WOKO website/wgzimmer for rooms available in Zurich. Whenever a new room is available, the script sends a push notification to phones properly set-up (in a subscriber / publisher fashion).

Assuming you already have an available VM on the cloud (if you don't, get one ASAP), deploying this script requires ~5 mins.

## Running the Script

Steps for running the script locally are:

1. `pip3 install -r requirements.txt`.
2. Install the push-notification app companion, [**Ntfy.sh**](https://ntfy.sh/). The Android app is [here](https://play.google.com/store/apps/details?id=io.heckel.ntfy).
3. Open the **Ntfy.sh** app, and add subscribe to the topic "_cazare_woko_" (or whatever string you replaced it with at the top of [scraper.py](./scraper.py)).
4. Run the `run.sh` script
5. ???
6. Enjoy

## Running the script on the cloud

I highly recommend running the script on a cloud VM. This ensures the script runs 100% of the time.

As it's really tiny, any VM will work, including the free ones given by AWS or Oracle Cloud (I ran this script on an Oracle Cloud instance with one CPU and 1GB of RAM). The steps to do so are:

1. Create the VM.
2. SSH into the VM.
3. Clone the repository `git clone https://github.com/theodormoroianu/WOKO_New_Room_Notification`.
4. Install `pip3 install -r requirements.txt`
