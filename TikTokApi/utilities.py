import subprocess
import sys

LOGGER_NAME: str = "TikTokApi"


def update_messager():
    if not check("TikTokApi"):
        # Outdated
        print(
            "TikTokApi package is outdated, please consider upgrading! \n(You can suppress this by setting ignore_version=True in the TikTokApi constructor)"
        )

    if not check_future_deprecation():
        print(
            "Your version of python is going to be deprecated, for future updates upgrade to 3.7+"
        )


def check(name):
    latest_version = str(
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "{}==random".format(name)],
            capture_output=True,
            text=True,
        )
    )
    latest_version = latest_version[latest_version.find("(from versions:") + 15:]
    latest_version = latest_version[: latest_version.find(")")]
    latest_version = latest_version.replace(" ", "").split(",")[-1]

    current_version = str(
        subprocess.run(
            [sys.executable, "-m", "pip", "show", "{}".format(name)],
            capture_output=True,
            text=True,
        )
    )
    current_version = current_version[current_version.find("Version:") + 8:]
    current_version = current_version[: current_version.find("\\n")].replace(" ", "")

    return latest_version == current_version


def check_future_deprecation():
    return sys.version_info >= (3, 7)
