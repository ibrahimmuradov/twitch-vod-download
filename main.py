from stream_vod_download import *


def main():
    vod_url = input_vod_url()
    save_network_logs(vod_url)

    stream_network_url = get_stream_network_url()
    if stream_network_url is None:
        raise Exception("Please try again")

    save_stream_vod(stream_network_url)


if __name__ == "__main__":
    main()
