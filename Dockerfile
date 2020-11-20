FROM mcr.microsoft.com/playwright:focal

RUN apt-get update && apt-get install -y python3-pip

RUN pip3 install TikTokApi
