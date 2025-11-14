import os
import httpx

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_GEOCODING_URL = "https://maps.apigw.ntruss.com/map-geocode/v2/geocode"

async def get_coordinates_from_address(address: str):
    """
    NAVER Maps API(Geocoding)를 사용하여 주소를 경도와 위도 좌표로 변환하는 함수
    - return: 경도(x), 위도(y) / None
    """
    
    if not address:
        print(f"주소 변환에 실패했습니다: address={address}")
        return None
    
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        print("NAVER Maps API 인증 정보(Client ID/Secret)가 설정되지 않았습니다.")
        return None
    
    headers = {
        "x-ncp-apigw-api-key-id": NAVER_CLIENT_ID,
        "x-ncp-apigw-api-key": NAVER_CLIENT_SECRET,
        "Accept": "application/json"
    }
    params = {
        "query": address
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(NAVER_GEOCODING_URL, headers=headers, params=params, timeout=5.0)
            
            if response.status_code != 200:
                print(f"NAVER Maps API 요청 실패(address={address}): [{response.status_code}] {response.text}")
                return None
            
            data = response.json()
            status = data.get("status", "UNKNOWN")
            
            if status == "OK" and data.get("addresses"):
                addr = data["addresses"][0]
                x = float(addr.get("x", -1.0)) # 경도
                y = float(addr.get("y", -1.0)) # 위도
                return x, y
            else:
                message = data.get("errorMessage", "-")
                print(f"NAVER Maps API 주소 변환 실패(address={address}): status={status}, error={message}")
                return None
    
    except httpx.ReadTimeout:
        print(f"NAVER Maps API 타임아웃(address={address})")
        return None
    except httpx.RequestError as e:
        print(f"네트워크 오류 발생(address={address}): {e}")
        return None
    except ValueError as e:
        print(f"JSON 파싱 오류(address={address}): {e}")
        return None
    except Exception as e:
        print(f"NAVER Maps API 요청 중 알 수 없는 오류 발생(address={address}): {e}")
        return None