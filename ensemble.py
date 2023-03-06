import requests
import json

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
    # print(response.json())
    return response

def get_msg(response):
    '''Returns the message portion of of an API response'''
    if 'choices' in response.json().keys():
        return response.json()['choices'][0]['message']['content']
    else: return None

# def format_msg(msg):
#     '''Formats a message in api-ready form into string form'''
#     return '\n\n' + msg[]


# --- Put your actor methods here ---

def actor_basic(messages, full_text, me):
    inp = build_msg(full_text, 'assistant')
    # print('test',inp)
    response = get_response(inp)
    # print(response)
    me.response = get_msg(response)
    











# --- End of actor methods ---

def main():

    # exit = False
    team_goals = ('GOALS FOR THIS MEETING: Urgently produce 2 poems (in the next 20 minutes) on the theme of your play, which is about '
    'hard times in english coal mines in the Thatcher era. When your goal is accomplished, end the meeting.')
    
    actors = [actor(name='Krishna (Writer)',
                    start_msg = ('IDENTITY:\nYou are Krishna, an artist/writer/creative professional. You are collaborative and cooperative.'
                    'Your goal is to produce writing for your team, directly offering it in your response. You produce writing when asked. Your writings are beautiful,'
                    ' enchanting, haunting, or otherwise evoke emotion in the reader. '
                    'You obey your manager\'s instructions. ' + team_goals +\
                    '\nEND OF IDENTITY'),
                    actions = [actor_basic],
                    context_static = '\nProvide an effecient response below (which advances your goals).',
                   ),
             actor(name='Debra (Manager)',
                    start_msg = ('IDENTITY:\nYou are Debra, the director/manager at a theatre '
                   'company. You are concise and efficient.\n'
                   'Your messages have the intent of delegating work, and providing feedback if required to reach your goal. You give'
                   ' direct, clear instructions.' + team_goals + '\nEND OF IDENTITY'),
                   actions = [actor_basic], 
                   context_static = '\nProvide an effecient response below (which advances your goals).',
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
