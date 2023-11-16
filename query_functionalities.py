"""
contains functions that enble user query the uploaded files and recieve
correct responses. The chatbot functionality is built using panel which is a
powerful yet simple and flexible python library for building interactive dashborads. 
it provided the needed bind tools that bound actions with their functions
in a clean manner in the project.
"""
import panel as pn
import param

from load_embed_retrieve import load_db

class cb_funcs(param.Parameterized):
    """
    call the load function, process files into vectordb
    create query, response function
    """
    chat_history = param.List([])
    answer = param.String("")
    db_query  = param.String("")
    db_response = param.List([])
    
    def __init__(self,  **params):
        super(cbfs, self).__init__( **params)
        self.panels = []
        self.loaded_file = "/path/to/file"
        self.qa = load_db(self.loaded_file,"stuff", 4)
    
    def call_load_db(self, count):
        """process user file"""
        if count == 0 or file_input.value is None:
            return pn.pane.Markdown(f"Loaded File: {self.loaded_file}")
        else:
            file_input.save("temp.pdf")  # local copy
            self.loaded_file = file_input.filename
            button_load.button_style="outline"
            self.qa = load_db("temp.pdf", "stuff", 4)
            button_load.button_style="solid"
        self.clr_history()
        return pn.pane.Markdown(f"Loaded File: {self.loaded_file}")

    @pn.cache(per_session=True)
    def convchain(self, query):
        """provide responses to user query"""
        if not query:
            return pn.WidgetBox(pn.Row('User:', pn.pane.Markdown("", width=600)), scroll=True)
        result = self.qa({"question": query, "chat_history": self.chat_history})
        self.chat_history.extend([(query, result["answer"])])
        self.db_query = result["generated_question"]
        self.db_response = result["source_documents"]
        self.answer = result['answer']

        user_pane = pn.pane.Markdown(query, width=600)
        chatbot_pane = pn.pane.Markdown(self.answer, width=1200, styles={'background-color': '#F6F6F6'})

        self.panels.extend([
            pn.Row('User:', user_pane),
            pn.Row('ChatBot:', chatbot_pane)
            ])

        inp.value = ''  #clears loading indicator
        return pn.WidgetBox(*self.panels, scroll=True)

    @param.depends('convchain', 'clr_history') 
    def get_chats(self):
        """keep tab of chat history"""
        if not self.chat_history:
            return pn.WidgetBox(pn.Row(pn.pane.Str("No History Yet")), width=600, scroll=True)
        rlist=[pn.Row(pn.pane.Markdown(f"Current Chat History variable", styles={'background-color': '#F6F6F6'}))]
        for exchange in self.chat_history:
            rlist.append(pn.Row(pn.pane.Str(exchange)))
        return pn.WidgetBox(*rlist, width=600, scroll=True)

    def clr_history(self,count=0):
        """clear chat history"""
        self.chat_history = []
        return

# build chat interface    
cb = cb_funcs()    
file_input = pn.widgets.FileInput(accept='.pdf')
button_load = pn.widgets.Button(name="Load DB", button_type='primary')
button_clearhistory = pn.widgets.Button(name="Clear History", button_type='warning')
button_clearhistory.on_click(cb.clr_history)
inp = pn.widgets.TextInput( placeholder='Enter text here…')

bound_button_load = pn.bind(cb.call_load_db, button_load.param.clicks)
chat = pn.bind(cb.convchain, inp) 

jpg_pane = pn.pane.Image( './img/convchain.jpg')

tab1 = pn.Column(
    pn.Row(inp),
    pn.layout.Divider(),
    pn.panel(chat,  loading_indicator=True),
    pn.layout.Divider(),
)

tab2= pn.Column(
    pn.panel(cb.get_chats),
    pn.layout.Divider(),
)
tab3=pn.Column(
    pn.Row( file_input, button_load, bound_button_load),
    pn.Row( button_clearhistory, pn.pane.Markdown("Clears chat history. Can use to start a new topic" )),
    pn.layout.Divider(),
    pn.Row(jpg_pane.clone(width=400))
)
dashboard = pn.Column(
    pn.Row(pn.pane.Markdown('# QueryYourData')),
    pn.Tabs(('Chat', tab1), ('Chat History', tab2), ('upload files', tab3))
)
dashboard.servable()
