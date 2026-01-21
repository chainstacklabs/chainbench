import time
from locust import HttpUser, task, between


class StreamingPerformanceUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def test_streaming_metrics(self):
        url = "/your-streaming-endpoint"

        # 1. Start overall timer
        start_perf = time.perf_counter()

        with self.client.get(url, stream=True, catch_response=True) as response:
            # 2. TTFB Calculation
            # response is available as soon as headers are received
            ttfb_ms = (time.perf_counter() - start_perf) * 1000

            # Manually report TTFB to the Locust UI
            self.environment.events.request.fire(
                request_type="STREAM",
                name=f"{url} [TTFB]",
                response_time=ttfb_ms,
                response_length=0,
                exception=None,
            )

            # 3. Consume the stream to measure download time
            bytes_received = 0
            try:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        bytes_received += len(chunk)

                # 4. Total Download Time Calculation
                total_time_ms = (time.perf_counter() - start_perf) * 1000

                # Manually report Total Time to the Locust UI
                self.environment.events.request.fire(
                    request_type="STREAM",
                    name=f"{url} [TOTAL]",
                    response_time=total_time_ms,
                    response_length=bytes_received,
                    exception=None,
                )
                response.success()

            except Exception as e:
                response.failure(str(e))