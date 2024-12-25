from openai import OpenAI
import random
import time

class Request:
    def __init__(self,config):
        self.config = config
        self.openai = OpenAI(
            api_key=self.config['deepinfra_api_key'],
            base_url=self.config['deepinfra_base_url']
        )

    def deepinfra_request(self,user,system=None,message=None):
        if system:
            message = [{"role":"system", "content":str(system)}, {"role":"user", "content":str(user)}]
        else:
            message = [{"role":"user", "content": str(user)}]

        for delay_secs in (2**x for x in range(0,10)):
            try:
                response = self.openai.chat.completions.create(
                    model="meta-llama/Meta-Llama-3.1-70B-Instruct",
                    messages=message,
                    temperature=0.2,
                )
                break
            except Exception as e:
                randomness_collision_avoidance = random.randint(0, 1000) / 1000.0
                sleep_dur = delay_secs + randomness_collision_avoidance
                print(f"Error: {e}. Retrying in {round(sleep_dur, 2)} seconds.")
                time.sleep(sleep_dur)
                continue

        return response.choices[0].message.content
    
    def request(self, user, system=None, message=None):
        response = self.deepinfra_request(user, system,message)
        return response
    