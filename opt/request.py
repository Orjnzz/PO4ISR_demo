import openai
import random
import time
from groq import Groq

class Request():
    def __init__(self, config):
        self.config = config
        self.apis = [Groq(api_key=key) for key in config['openai_api_key']]
        self.models = config['models']
        self.daily_token_limits = config['daily_token_limits']
        self.current_api_index = 0  # Start with the first API
        self.total_tokens_used = [0] * len(self.apis)  # Track tokens used for each API
        self.token_log = [[] for _ in range(len(self.apis))]  # Log for each API separately
        self.cumulative_tokens_used = 0  # Track total tokens used across all APIs
        self.max_retries = 5

    def request(self, user, system=None, message=None):
        return self.openai_request(user, system, message)
    
    def openai_request(self, user, system=None, message=None):
        # Prepare message list
        if system:
            message = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        else:
            content = system + user if system else user
            message = [{"role": "user", "content": content}]
        
        retries = 0
        while retries < self.max_retries:
            # Check if current API has exceeded its daily token limit
            if self.total_tokens_used[self.current_api_index] >= self.daily_token_limits[self.current_api_index]:
                print(f"API {self.current_api_index + 1} reached its daily token limit.")
                # Move to the next API in the list if available
                self.current_api_index += 1
                if self.current_api_index >= len(self.apis):
                    print("All APIs have reached their daily token limits. Exiting.")
                    return None  # Handle as needed when all APIs are exhausted

            # Select the active API and model based on the current index
            active_api = self.apis[self.current_api_index]
            model = self.models[self.current_api_index]
            
            try:
                response = active_api.chat.completions.create(
                    model=model,
                    messages=message,
                    temperature=0.2
                )
                
                # Extract and accumulate tokens used for the active API
                if hasattr(response, "usage"):
                    tokens_used = response.usage.total_tokens
                    self.total_tokens_used[self.current_api_index] += tokens_used
                    self.cumulative_tokens_used += tokens_used  # Update cumulative total
                    print(f"Tokens used in this request: {tokens_used}")
                    print(f"Cumulative total tokens used: {self.cumulative_tokens_used}")

                    # Log tokens used for testing
                    self.token_log[self.current_api_index].append(self.total_tokens_used[self.current_api_index])
                    
                return response.choices[0].message.content

            except Exception as e:
                if "rate limit" in str(e).lower():
                    print(f"Rate limit reached for API {self.current_api_index + 1}: {e}. Pausing for cooldown...")
                    time.sleep(360)  # Pause for 1 hour, or adjust as needed
                    retries += 1
                else:
                    delay_secs = 2 ** retries + random.uniform(0, 1)
                    print(f"Error: {e}. Retrying in {round(delay_secs, 2)} seconds.")
                    time.sleep(delay_secs)
                    retries += 1

        print("Max retries reached. Exiting.")
        return None  # Handle as needed if max retries are reached


# class Request():
#     def __init__(self, config):
#         self.config = config
#         self.api = Groq(api_key=self.config['openai_api_key'])
#         self.total_tokens_used = 0  # Initialize cumulative token counter
#         self.token_log = []  # Store cumulative token count for testing instead of using wandb
    
#     def request(self, user, system=None, message=None):
#         response = self.openai_request(user, system, message)
#         return response
    
#     def openai_request(self, user, system=None, message=None):
#         # Prepare messages list
#         if system:
#             message = [{"role": "system", "content": system}, {"role": "user", "content": user}]
#         else:
#             content = system + user if system else user
#             message = [{"role": "user", "content": content}]
        
#         model = self.config['model']
        
#         for delay_secs in (2**x for x in range(0, 10)):
#             try:
#                 response = self.api.chat.completions.create(
#                     model=model,
#                     messages=message,
#                     temperature=0.2
#                 )
#                 # Extract and accumulate total tokens used
#                 if hasattr(response, "usage"):
#                     tokens_used = response.usage.total_tokens
#                     self.total_tokens_used += tokens_used  # Update cumulative token count
#                     print(f"Tokens used in this request: {tokens_used}")
#                     print(f"Cumulative total tokens used: {self.total_tokens_used}")

#                     # Log cumulative token count for testing
#                     self.token_log.append(self.total_tokens_used)
#                     print(f"Logged cumulative tokens for testing: {self.token_log}")
#                 break
#             except Exception as e:
#                 randomness_collision_avoidance = random.randint(0, 1000) / 1000.0
#                 sleep_dur = delay_secs + randomness_collision_avoidance
#                 print(f"Error: {e}. Retrying in {round(sleep_dur, 2)} seconds.")
#                 time.sleep(sleep_dur)
#                 continue
        
#         # Return the response content
#         return response.choices[0].message.content

# class Request():
#     def __init__(self, config):
#         self.config = config
#         self.api = Groq(api_key=self.config['openai_api_key'])
#         self.alternative_api = Groq(api_key=self.config['alternative_api_key']) if config.get('use_alternative_api') else None
#         self.total_tokens_used = 0  # Initialize cumulative token counter
#         self.token_log = []  # Store cumulative token count for testing instead of using wandb
#         self.max_retries = 5  # Set a max retry limit
#         self.daily_token_limit = 500000  # Daily token limit for the primary API
#         self.using_alternative_api = False  # Track which API is active

#     def request(self, user, system=None, message=None):
#         response = self.openai_request(user, system, message)
#         return response
    
#     def openai_request(self, user, system=None, message=None):
        # Check if daily token limit is reached
        # if not self.using_alternative_api and self.total_tokens_used >= self.daily_token_limit:
        #     self.using_alternative_api = True

        # # Use the appropriate API based on the current state
        # active_api = self.alternative_api if self.using_alternative_api else self.api
        # model = self.config['alternative_model'] if self.using_alternative_api else self.config['model']
        
        # # Prepare messages list
        # if system:
        #     message = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        # else:
        #     content = system + user if system else user
        #     message = [{"role": "user", "content": content}]
        
        # retries = 0
        # while retries < self.max_retries:
        #     try:
        #         response = active_api.chat.completions.create(
        #             model=model,
        #             messages=message,
        #             temperature=0.2
        #         )
                
        #         # Extract and accumulate total tokens used
        #         if hasattr(response, "usage"):
        #             tokens_used = response.usage.total_tokens
        #             self.total_tokens_used += tokens_used  # Update cumulative token count
        #             print(f"Tokens used in this request: {tokens_used}")
        #             print(f"Cumulative total tokens used: {self.total_tokens_used}")

        #             # Log cumulative token count for testing
        #             self.token_log.append(self.total_tokens_used)
        #         return response.choices[0].message.content

        #     except Exception as e:
        #         if "rate limit" in str(e).lower():
        #             print(f"Rate limit reached: {e}. Pausing for cooldown...")
        #             time.sleep(3600)  # Pause for 1 hour, or adjust as needed
        #             retries += 1
        #         else:
        #             randomness_collision_avoidance = random.uniform(0, 1)
        #             delay_secs = 2 ** retries + randomness_collision_avoidance
        #             print(f"Error: {e}. Retrying in {round(delay_secs, 2)} seconds.")
        #             time.sleep(delay_secs)
        #             retries += 1

        # print("Max retries reached. Exiting.")
        # return None

# class Request():
#     def __init__(self, config):
#         self.conifg = config
#         openai.api_key = self.conifg['openai_api_key']
    
#     def request(self, user, system=None, message=None):
#         response = self.openai_request(user, system, message)

#         return response
    
#     def openai_request(self, user, system=None, message=None):
#         '''
#         fix openai communicating error
#         https://community.openai.com/t/openai-error-serviceunavailableerror-the-server-is-overloaded-or-not-ready-yet/32670/19
#         '''
#         if system:
#             message=[{"role":"system", "content":system}, {"role": "user", "content": user}]
#         else:
#             content = system + user
#             message=[{"role": "user", "content": content}]
#         model = self.conifg['model']
#         for delay_secs in (2**x for x in range(0, 10)):
#             try:
#                 response = openai.ChatCompletion.create(
#                     model=model,
#                     messages = message,
#                     temperature=0.2,
#                     frequency_penalty=0.0)
#                 break
#             except openai.OpenAIError as e:
#                 randomness_collision_avoidance = random.randint(0, 1000) / 1000.0
#                 sleep_dur = delay_secs + randomness_collision_avoidance
#                 print(f"Error: {e}. Retrying in {round(sleep_dur, 2)} seconds.")
#                 time.sleep(sleep_dur)
#                 continue
        
#         return response["choices"][0]["message"]["content"]