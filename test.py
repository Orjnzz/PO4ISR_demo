import os
import wandb
from opt.eval import Eval
from opt.config import init_config
from opt.utils import load_eval_data


if __name__ == '__main__':
    test_prompt = "Based on the user's current session interactions, you need to answer the following subtasks step by step:\n" \
                   "1. Analyze the session context and specific details of the interactions to identify combinations of items.\n"\
                   "2. Determine the user's interactive intent for each combination, taking into account their past interactions and preferences.\n"\
                   "3. Choose the intent that best represents the user's current needs and desires, considering the context and specific details of the interactions.\n"\
                   "4. Finally, reorder the 20 items in the candidate set based on the selected intent, taking into consideration the possibility of potential user interactions.\n"\
                   "Provide the ranking results with the item index, ensuring that the order of all items in the candidate set is provided."
    
    conf = init_config()
    test_data = load_eval_data(conf)

    key = conf['openai_api_key']
    if conf['use_wandb']:
        wandb.login(key=conf['wandb_api_key'])
        conf.pop('openai_api_key')
        run = wandb.init(
            project=f"PO4ISR_{conf['dataset']}_test",
            config=conf,
            name=f"seed_{conf['seed']}",
        )
        text_table = wandb.Table(columns=["Input", "Target", "Response"])
    else:
        text_table = None
    conf['openai_api_key'] = key

    eval_model = Eval(conf, test_data, text_table)
    results, target_rank_list, error_list = eval_model.run(test_prompt)

    result_save_path = f"./res/metric_res/{conf['dataset']}/"
    if not os.path.exists(result_save_path):
        os.makedirs(result_save_path)
    results.to_csv(f"{result_save_path}seed_{conf['seed']}_nir_po4_3.csv", index=False)
    
    if conf['use_wandb']:
        run.log({"texts": text_table})