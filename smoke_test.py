from utils.file_parser import parse_txt
from utils.system_monitor import get_full_status, format_status_text
from utils.logger import log_info, get_logs

sample = b"atmospheric optics weak signal spectral analysis atmospheric visualization"
parsed = parse_txt(sample, "sample.txt")
assert parsed["success"]
assert "atmospheric" in parsed["text"]

status = get_full_status()
text = format_status_text(status, "en")
assert "CPU" in text

log_info("smoke test log entry")
assert "smoke test" in get_logs()

print("AOAA smoke test passed.")
