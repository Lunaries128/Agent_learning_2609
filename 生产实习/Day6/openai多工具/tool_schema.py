tool_schema = [
    {
        "type": "function",
        "function": {
            "name":"get_weather",
            "description":"获取指定城市的天气信息",
            "parameters":{
                "type":"object",
                "properties":{
                    "city":{
                        "type":"string",
                        "description":"城市的名称"
                    }
                }
            },
            "required":["city"]
        }
    },
    {
        "type": "function",
        "function": {
            "name":"get_clothing_advice",
            "description":"根据天气的数据给出穿衣的建议",
            "parameters":{
                "type":"object",
                "properties":{
                    "temperature":{
                        "type":"number",
                        "description":"温度(摄氏度)"
                    },
                    "rain_probability":{
                        "type":"number",
                        "description":"降雨概率(0-100)"
                    },
                    "nv_index":{
                        "type":"number",
                        "description":"紫外线强度(0-11)"
                    }
                }
            },
            "required":["temperature","rain_probability","nv_index"]
        }
    },
    {
        "type": "function",
        "function": {
            "name":"get_travel_advice",
            "description":"根据天气信息以及温度推荐出行方式",
            "parameters":{
                "type":"object",
                "properties":{
                    "weather_conditon":{
                        "type":"string",
                        "description":"天气信息，例如:晴、多云、小雨、大雨、雪"
                    },
                    "temperature":{
                        "type":"number",
                        "description":"温度(摄氏度)"
                    }
                }
            },
            "required":["weather_conditon","temperature"]
        }
    }
]