
import json



def safe_get(data, *args):
    """
    Get the data from the data object
    """
    for arg in args:
        try:
            data = data[arg]
        except (IndexError, TypeError, KeyError):
            return None
    return data


def get_complete_address(data):
    """
    Get the complete address from the data object
    """
    ward = safe_get(data, 6, 183, 1, 0)
    street = safe_get(data, 6, 183, 1, 1)
    city = safe_get(data, 6, 183, 1, 3)
    postal_code = safe_get(data, 6, 183, 1, 4)
    state = safe_get(data, 6, 183, 1, 5)
    country_code = safe_get(data, 6, 183, 1, 6)

    result = {
        'ward': ward,
        'street': street,
        'city': city,
        'postal_code': postal_code,
        'state': state,
        'country_code': country_code
    }
    return result


def parse(response, link):
    """
    Get the data from the input_str
    """
    if response and response.status_code == 200:
        initialization_state_part = response.text.split(';window.APP_INITIALIZATION_STATE=')[1]
        app_initialization_state = initialization_state_part.split(';window.APP_FLAGS')[0]
        
        json_str = json.loads(app_initialization_state)[3][6]
        if json_str.startswith(")]}'"):
            json_str = json_str[4:]
        data = json.loads(json_str)
        
        place_id = safe_get(data, 6, 78)
        place_name = safe_get(data, 6, 11)
        place_desc =  safe_get(data, 6, 32, 1, 1)
        place_reviews = safe_get(data, 6, 4, 8)
        place_website = safe_get(data, 6, 7, 0)
        place_owner = safe_get(data, 6, 57, 1)
        place_main_category = safe_get(data, 6, 13, 0)
        place_categories = safe_get(data, 6, 13)
        place_rating = safe_get(data, 6, 4, 7)
        place_phone = safe_get(data, 6, 178, 0, 0)
        place_address = safe_get(data, 6, 18)
        place_detailed_address = get_complete_address(data)
        place_timezone = safe_get(data, 6, 30)
        place_gmap_link = link

        return {
            'place_id': place_id,
            'place_name': place_name,
            'place_desc': place_desc,
            'place_reviews': place_reviews,
            'place_website': place_website,
            'place_owner': place_owner,
            'place_main_category': place_main_category,
            'place_categories': place_categories,
            'place_rating': place_rating,
            'place_phone': place_phone,
            'place_address': place_address,
            'place_detailed_address': place_detailed_address,
            'place_timezone': place_timezone,
            'place_gmap_link': place_gmap_link
        }




import requests

cookies = {
    'SID': 'dQjLUUCLKOdMfNLBN6S0_jCuAQhbTWNyY2XxCY8vDFlPGPa8Vq6vdAdfPvK5nrStVp7Czw.',
    '__Secure-1PSID': 'dQjLUUCLKOdMfNLBN6S0_jCuAQhbTWNyY2XxCY8vDFlPGPa8F4n0Aowyy68P3b4UOKh_kg.',
    '__Secure-3PSID': 'dQjLUUCLKOdMfNLBN6S0_jCuAQhbTWNyY2XxCY8vDFlPGPa8ye3jWGZxhCu3SPHuXKEfew.',
    'HSID': 'AfK_X7Lw9Vw-1-8kf',
    'SSID': 'A9Nbqk905QzR7tivf',
    'APISID': 'V_NQCL-9SDFbe-YE/A3DSpcu2TQC49oyL6',
    'SAPISID': 'o8Alr0Y6yahgvkJZ/As8t7VLOEVQynL7lq',
    '__Secure-1PAPISID': 'o8Alr0Y6yahgvkJZ/As8t7VLOEVQynL7lq',
    '__Secure-3PAPISID': 'o8Alr0Y6yahgvkJZ/As8t7VLOEVQynL7lq',
    'OTZ': '7304299_36_36__36_',
    '__Secure-ENID': '16.SE=Ll-4mjma4_BWyLFiusi8wgqrNzKLwI1m7RXx84MXAsaN_gOdjvpq-e873na73AkFCYGTotFg1cEs-TLlr1nYi0-T4w11BK8fPbG-U8l7E82GVVNVoDH_vksvjVHwnOH6AnOrlMBV6hADUZAMK0E0DGRZRV6qncNYZRi9gU6yNya1PVI6lwyNOMB3r7KYgu3f14OyXnPh4KfblL_HlrN42CBhEuAKQp2yxoy177fv8DYBug_iOtz5lD8opZpaqijcrZTtBoIZTGp9FnU',
    'AEC': 'Ackid1Tgd7puDMxVd7p97xd0J5yw6XHzq5ddoeLXun9ZpaaY650Sn9pv9g',
    'SEARCH_SAMESITE': 'CgQI6ZkB',
    '1P_JAR': '2023-11-29-02',
    'NID': '511=AQCxYrx2QtEAR3S81Mp2HqCR8ydi0Jfwyve6BLWo2bjzB_KVGHeFmveZ7zeUspjg9pENNg4hTZOmAypOd0a59FlWyvaV1oneX0ESRXykW_PpyPraPEfduzJKdM8Y9MQYZw9Kk1-vojEF2d-JrlQ9Gl9-FuaDHxtSQXSePQYgQbgrPMlT9TVZKHA_2WJAxnpa9Dj-au5jgl3bg04T0ev3uuL_AAq5_C3rFlOIrMAQpkRQJWAcnd5P34Td8BV_CHhzYUXZklJX1XfIWluK9FlEaoxUVGYCYp5HInAyxyRce6XS_MIcIdAv01hrVwOVj9XPlijuLscNc4UbX90EHzBNlKkroOdnPNTX9q8ZDpKWJtvEA5JJDnFQIjeJtOva68-KdDYh9WxVE_NeifXNmn71iZ9-pq3QJSsFr0dmejWAh5njoux0lXyR49MS4nLc3JJNAVaoFOAaPicN3AJrP8jFX9cE8zfp1dpWYpFYfw5wJFu2_IL5uGuVOy2E_6W0hU-xpSmsxLm55C6vENLl2d9qjqqfaMg5OoWmc2p-a6GJOeNP_CSPNBDL7zJfTJeqCWL5RKHgFCwDgzcur9pG2NqC-pIN1U7GaGkz1DTc9FriYvt-VA',
    '__Secure-1PSIDTS': 'sidts-CjEBNiGH7vvHwgGzatf4806jTgGYlLbSyYoveUkXLaBjUmg7OdFIGhn1yhFTnZ-VtFhaEAA',
    '__Secure-3PSIDTS': 'sidts-CjEBNiGH7vvHwgGzatf4806jTgGYlLbSyYoveUkXLaBjUmg7OdFIGhn1yhFTnZ-VtFhaEAA',
    'SIDCC': 'ACA-OxMIHLUSc9K0bIHGx4c9uTsIg_c-9VAVujIzdGV8qDi6yKV2plkwsTDLKtwARj4t_TTWpg',
    '__Secure-1PSIDCC': 'ACA-OxMyj7iLHrUMOZA9CPvXXnq1qi4ttsJ4mXpJt-G9pYT10AhBG-L5aw6OUKv5-lB90O-5_GI',
    '__Secure-3PSIDCC': 'ACA-OxN-Mu6FBzK1KhWy1NQfYqZxVVbySAhxZqc9sh_JSN1uEXFKA3fUrnRt-Y_s641u-LPx_PI',
}

headers = {
    'Host': 'www.google.com',
    'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Sec-Ch-Ua-Arch': '"x86"',
    'Sec-Ch-Ua-Full-Version': '"119.0.6045.123"',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Ch-Ua-Platform-Version': '"6.5.6"',
    'Sec-Ch-Ua-Bitness': '"64"',
    'Sec-Ch-Ua-Full-Version-List': '"Google Chrome";v="119.0.6045.123", "Chromium";v="119.0.6045.123", "Not?A_Brand";v="24.0.0.0"',
    'Sec-Ch-Ua-Model': '""',
    'Sec-Ch-Ua-Wow64': '?0',
    'Sec-Ch-Ua-Platform': '"Linux"',
    'X-Client-Data': 'CIy2yQEIprbJAQipncoBCNjbygEIlqHLAQiHoM0BGPXJzQEY1NzNARin6s0B',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.google.com/',
    # 'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,ur;q=0.8',
    # 'Cookie': 'SID=dQjLUUCLKOdMfNLBN6S0_jCuAQhbTWNyY2XxCY8vDFlPGPa8Vq6vdAdfPvK5nrStVp7Czw.; __Secure-1PSID=dQjLUUCLKOdMfNLBN6S0_jCuAQhbTWNyY2XxCY8vDFlPGPa8F4n0Aowyy68P3b4UOKh_kg.; __Secure-3PSID=dQjLUUCLKOdMfNLBN6S0_jCuAQhbTWNyY2XxCY8vDFlPGPa8ye3jWGZxhCu3SPHuXKEfew.; HSID=AfK_X7Lw9Vw-1-8kf; SSID=A9Nbqk905QzR7tivf; APISID=V_NQCL-9SDFbe-YE/A3DSpcu2TQC49oyL6; SAPISID=o8Alr0Y6yahgvkJZ/As8t7VLOEVQynL7lq; __Secure-1PAPISID=o8Alr0Y6yahgvkJZ/As8t7VLOEVQynL7lq; __Secure-3PAPISID=o8Alr0Y6yahgvkJZ/As8t7VLOEVQynL7lq; OTZ=7304299_36_36__36_; __Secure-ENID=16.SE=Ll-4mjma4_BWyLFiusi8wgqrNzKLwI1m7RXx84MXAsaN_gOdjvpq-e873na73AkFCYGTotFg1cEs-TLlr1nYi0-T4w11BK8fPbG-U8l7E82GVVNVoDH_vksvjVHwnOH6AnOrlMBV6hADUZAMK0E0DGRZRV6qncNYZRi9gU6yNya1PVI6lwyNOMB3r7KYgu3f14OyXnPh4KfblL_HlrN42CBhEuAKQp2yxoy177fv8DYBug_iOtz5lD8opZpaqijcrZTtBoIZTGp9FnU; AEC=Ackid1Tgd7puDMxVd7p97xd0J5yw6XHzq5ddoeLXun9ZpaaY650Sn9pv9g; SEARCH_SAMESITE=CgQI6ZkB; 1P_JAR=2023-11-29-02; NID=511=AQCxYrx2QtEAR3S81Mp2HqCR8ydi0Jfwyve6BLWo2bjzB_KVGHeFmveZ7zeUspjg9pENNg4hTZOmAypOd0a59FlWyvaV1oneX0ESRXykW_PpyPraPEfduzJKdM8Y9MQYZw9Kk1-vojEF2d-JrlQ9Gl9-FuaDHxtSQXSePQYgQbgrPMlT9TVZKHA_2WJAxnpa9Dj-au5jgl3bg04T0ev3uuL_AAq5_C3rFlOIrMAQpkRQJWAcnd5P34Td8BV_CHhzYUXZklJX1XfIWluK9FlEaoxUVGYCYp5HInAyxyRce6XS_MIcIdAv01hrVwOVj9XPlijuLscNc4UbX90EHzBNlKkroOdnPNTX9q8ZDpKWJtvEA5JJDnFQIjeJtOva68-KdDYh9WxVE_NeifXNmn71iZ9-pq3QJSsFr0dmejWAh5njoux0lXyR49MS4nLc3JJNAVaoFOAaPicN3AJrP8jFX9cE8zfp1dpWYpFYfw5wJFu2_IL5uGuVOy2E_6W0hU-xpSmsxLm55C6vENLl2d9qjqqfaMg5OoWmc2p-a6GJOeNP_CSPNBDL7zJfTJeqCWL5RKHgFCwDgzcur9pG2NqC-pIN1U7GaGkz1DTc9FriYvt-VA; __Secure-1PSIDTS=sidts-CjEBNiGH7vvHwgGzatf4806jTgGYlLbSyYoveUkXLaBjUmg7OdFIGhn1yhFTnZ-VtFhaEAA; __Secure-3PSIDTS=sidts-CjEBNiGH7vvHwgGzatf4806jTgGYlLbSyYoveUkXLaBjUmg7OdFIGhn1yhFTnZ-VtFhaEAA; SIDCC=ACA-OxMIHLUSc9K0bIHGx4c9uTsIg_c-9VAVujIzdGV8qDi6yKV2plkwsTDLKtwARj4t_TTWpg; __Secure-1PSIDCC=ACA-OxMyj7iLHrUMOZA9CPvXXnq1qi4ttsJ4mXpJt-G9pYT10AhBG-L5aw6OUKv5-lB90O-5_GI; __Secure-3PSIDCC=ACA-OxN-Mu6FBzK1KhWy1NQfYqZxVVbySAhxZqc9sh_JSN1uEXFKA3fUrnRt-Y_s641u-LPx_PI',
}

params = {
    'authuser': '0',
    'hl': 'en',
    'rclk': '1',
}

response = requests.get(
    'https://www.google.com/maps/place/Rashi+Developers/data=!4m7!3m6!1s0x3bae16792310e53b:0x1f89f384fa2604ea!8m2!3d12.9714614!4d77.6008194!16s%2Fg%2F1vm_wb5h!19sChIJO-UQI3kWrjsR6gQm-oTziR8',
    params=params,
    cookies=cookies,
    headers=headers,
    verify=False,
)
print(parse(response, response.url))