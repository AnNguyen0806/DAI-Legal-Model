import json
import time
from pathlib import Path

import pandas as pd
import requests


BASE_DIR = Path(r"D:\DAI-Legal-Model")
TEST_FILE = BASE_DIR / "DAI_Legal_Model_Test_Cases_v1.xlsx"
OUTPUT_FILE = BASE_DIR / "DAI_Legal_Model_Test_Cases_Result.xlsx"

API_URL = "http://localhost:8000/api/v1/chat/completions"


def call_core_api(question):
    payload = {
        "prompt": question,
        "allow_external": False
    }

    try:
        response = requests.post(
            API_URL,
            json=payload,
            timeout=180
        )

        if response.status_code != 200:
            return f"API ERROR HTTP {response.status_code}"

        # Core API trả SSE
        answer = ""

        for line in response.text.splitlines():
            line = line.strip()

            if not line.startswith("data:"):
                continue

            raw = line[5:].strip()

            if not raw:
                continue

            try:
                data = json.loads(raw)

                if data.get("delta"):
                    answer += data["delta"]

            except json.JSONDecodeError:
                continue

        return answer.strip()

    except Exception as e:
        return f"REQUEST ERROR: {e}"


def check_result(actual, expected):
    actual = str(actual).strip().lower()
    expected = str(expected).strip().lower()

    if not actual:
        return "FAIL"

    # Các expected dạng số liệu quan trọng
    if expected == "1 ngày":
        return "PASS" if "1 ngày" in actual else "FAIL"

    if expected == "7 ngày làm việc":
        return "PASS" if "7 ngày" in actual else "FAIL"

    if expected == "129 ngày làm việc":
        return "PASS" if "129 ngày làm việc" in actual else "FAIL"

    if expected == "05 ngày làm việc":
        return "PASS" if (
            "05 ngày làm việc" in actual
            or "5 ngày làm việc" in actual
        ) else "FAIL"

    if expected == "0":
        return "PASS" if (
            "0" in actual
            or "không thu phí" in actual
            or "miễn phí" in actual
        ) else "FAIL"

    if expected == "trực tiếp":
        return "PASS" if "trực tiếp" in actual else "FAIL"

    if expected == "có, trực tuyến":
        return "PASS" if (
            "trực tuyến" in actual
            or "online" in actual
        ) else "FAIL"

    if expected == "không đồng":
        return "PASS" if "không đồng" in actual else "FAIL"

    # Các test yêu cầu thông tin/thành phần hồ sơ:
    # chỉ đánh giá API có trả lời hay không ở vòng test đầu.
    if "thông tin tổng hợp" in expected.lower():
        return "PASS" if len(actual) > 20 else "FAIL"

    if "thành phần hồ sơ" in expected.lower():
        keywords = [
            "hồ sơ",
            "giấy tờ",
            "bản chính",
            "bản sao",
            "căn cước",
            "đơn"
        ]

        return "PASS" if any(k in actual for k in keywords) else "FAIL"

    if "theo dữ liệu thủ tục" in expected.lower():
        return "PASS" if len(actual) > 10 else "FAIL"

    if expected in actual:
        return "PASS"

    return "FAIL"


def main():
    print("=" * 70)
    print("DAI LEGAL MODEL - AUTOMATED TEST")
    print("=" * 70)

    if not TEST_FILE.exists():
        print(f"KHONG TIM THAY FILE:")
        print(TEST_FILE)
        return

    print(f"Test file: {TEST_FILE}")
    print(f"Core API : {API_URL}")
    print()

    df = pd.read_excel(TEST_FILE)

    required_columns = [
        "Test Case ID",
        "Question",
        "Expected Answer"
    ]

    for col in required_columns:
        if col not in df.columns:
            print(f"THIEU COLUMN: {col}")
            return

    results = []

    total = len(df)
    passed = 0

    print(f"TONG SO TEST: {total}")
    print()

    for index, row in df.iterrows():

        test_id = str(row["Test Case ID"])
        question = str(row["Question"])
        expected = str(row["Expected Answer"])

        print("=" * 70)
        print(f"[{index + 1}/{total}] {test_id}")
        print(f"QUESTION : {question}")
        print(f"EXPECTED : {expected}")

        start = time.time()

        actual = call_core_api(question)

        elapsed = time.time() - start

        result = check_result(actual, expected)

        if result == "PASS":
            passed += 1

        print(f"ACTUAL   : {actual}")
        print(f"RESULT   : {result}")
        print(f"TIME     : {elapsed:.2f}s")

        results.append({
            "Test Case ID": test_id,
            "Question": question,
            "Expected Answer": expected,
            "Actual Answer": actual,
            "Result": result,
            "Response Time (s)": round(elapsed, 2),
            "Notes": ""
        })

        # Nghỉ một chút để tránh gửi 21 request liên tục
        time.sleep(1)

    result_df = pd.DataFrame(results)

    accuracy = (passed / total * 100) if total else 0

    print()
    print("=" * 70)
    print("TEST COMPLETED")
    print("=" * 70)
    print(f"TOTAL : {total}")
    print(f"PASS  : {passed}")
    print(f"FAIL  : {total - passed}")
    print(f"ACCURACY: {accuracy:.2f}%")
    print("=" * 70)

    result_df.to_excel(
        OUTPUT_FILE,
        index=False,
        sheet_name="Test Results"
    )

    print()
    print(f"RESULT FILE:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()