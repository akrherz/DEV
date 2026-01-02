"""Check that my throttle is working..."""

import concurrent.futures

import httpx

URL = "http://iem.local/sites/obhistory.php?station=AMW&network=IA_ASOS"
NUM_REQUESTS = 100


def fetch():
    try:
        response = httpx.get(URL)
        return response.status_code
    except Exception as e:
        return f"Error: {e}"


def main():
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=NUM_REQUESTS
    ) as executor:
        futures = [executor.submit(fetch) for _ in range(NUM_REQUESTS)]
        for i, future in enumerate(
            concurrent.futures.as_completed(futures), 1
        ):
            print(f"Request {i}: {future.result()}")


if __name__ == "__main__":
    main()
