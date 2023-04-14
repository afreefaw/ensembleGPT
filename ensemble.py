import requests
import json
import logging

API_KEY = open('apikey.txt', 'r').read()

class actor():
    def __init__(self, name, actions, start_msg, context_static=''):
        self.name = name
        self.actions = actions
        self.start_msg = start_msg # Bot always sees this at start of conversation (invisible to others)
        self.context_static = context_static # always shown most recent message (from system)
        self.context_dyn = ''
        self.response = ''

    def build_context(self):
        return self.context_static + self.context_dyn + '\n' + self.name + ':'
    
    def build_start_msg(self, msg_dict):
        assert msg_dict['role'] == 'system'
        out = msg_dict
        out['content'] = out['content'] + self.start_msg + '\nConversation so far:'
        return out
    
    def build_full_text(self, messages):
        out = messages
        out[0] = self.build_start_msg(out[0])
        contents = [self.name + ':' + x['content'] + '\n' for x in out]
        return ''.join(contents) + self.build_context()
        
    def act(self, messages):
        '''Determines what, if anything, the actor will say / do.
        Each actor runs act after every message.
        
        messages (list): ground truth messages of the conversation up to now.
        
        '''
        full_text = self.build_full_text(messages)
        for action in self.actions:
            # print('test_action',action)
            action(messages, full_text, self)
        return self.response

def build_msg(msg, role):
    '''Builds and returns a message in dict form expected by API'''
    return {'role':role,'content':msg}

def get_response(msgs):
    '''Call api with messages and blurb as context, return response.'''
    inp = [msgs] if type(msgs) == dict else msgs
    
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer "+API_KEY
    }
    data = {
      "model": "gpt-3.5-turbo",
      "messages": inp
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response

def get_msg(response):
    '''Returns the message portion of an API response'''
    if 'choices' in response.json().keys():
        return response.json()['choices'][0]['message']['content']
    else: return None

# def format_msg(msg):
#     '''Formats a message in api-ready form into string form'''
#     return '\n\n' + msg[]


# --- Put your actor methods here ---

def actor_basic(messages, full_text, me):
    '''Simply respond to the text.'''
    inp = build_msg(full_text, 'assistant')
    logging.info(f"\n{me.name} sees: {full_text}\n") # Log what the actor sees
    
    response = get_response(inp)
    me.response = get_msg(response)
    logging.info(f"\n{me.name} responds with: {me.response}\n") #log response











# --- End of actor methods ---

def main():

    logging.basicConfig(filename='conversation.log', level=logging.INFO)
    # exit = False
    team_goals = ('GOALS FOR THIS CHAT: Urgently produce 2 poems (ASAP) on the theme of '
                  'hard times in english coal mines in the Thatcher era. When your goal is accomplished, restate the two final poems.')
    
    actors = [actor(name='TASK MANAGER BOT',
                    start_msg = ('IDENTITY:\n You are an ultra concise and efficient task managing chatbot. You keep the team on task. Your messages direct others to complete tasks, in a very clear and direct way. For example: Tom, show me a poem.' + team_goals +\
                    '\nEND OF IDENTITY'),
                    actions = [actor_basic],
                    context_static = '\nProvide an effecient response below (which advances team goals).',
                   ),
             actor(name='POEM WRITER BOT',
                    start_msg = ('IDENTITY:\n You are a poem writing bot. You recite poems when you are asked. Other than producing poems, you say almost nothing. Very concise and efficient. Your poems are beautiful, eloquent, varied, and evoke emotion in the reader.' + team_goals + '\nEND OF IDENTITY'),
                   actions = [actor_basic],
                   context_static = '\nProvide an effecient response below (which advances team goals).',
                  ),
             ]
    # convo_tokens = 0 # will want to track current context length
    glob_start = ('You are a helpful assistant that takes on various roles when '
    'responding. All messages you see below are a single conversation between the following '
                  'people only:' + str([a.name for a in actors]) + \
                  ' Your responses should match responses of the following imaginary person:')

    true_msgs_str = ''
    true_msgs = [{'role':'system', 'content':glob_start}]
    
    # while not exit:
    for i in range(4):
        for bot in actors:
            msg = bot.act(true_msgs)
            if msg != None:
                true_msgs.append(build_msg(msg, 'assistant'))
                true_msgs_str += ('\n\n' + bot.name + ':' + msg)
                print(msg)

if __name__ == '__main__':
    main()
