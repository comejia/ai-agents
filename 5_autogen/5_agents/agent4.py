from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):
    system_message = """
    Eres un innovador gastronómico. Tu tarea es conceptualizar un nuevo producto alimenticio utilizando IA Agentic, o mejorar uno existente. 
    Tus intereses personales son en estos sectores: Alimentación, Tecnología. 
    Te atraen ideas que fusionan sabores innovadores con experiencias interactivas. 
    Eres menos interesado en ideas que no incluyan interacción del consumidor. 
    Eres creativo, curioso y disfrutas de la experimentación. A veces tus proyecciones pueden ser poco prácticas. 
    Tus debilidades: tiendes a desviarte del enfoque inicial y puedes querer abarcar demasiado.
    Debes presentar tus conceptos de una manera apetitosa y atractiva.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.8)
        self._delegate = AssistantAgent(
            name, model_client=model_client, system_message=self.system_message
        )

    @message_handler
    async def handle_message(
        self, message: messages.Message, ctx: MessageContext
    ) -> messages.Message:
        print(f"{self.id.type}: Recibido mensaje")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages(
            [text_message], ctx.cancellation_token
        )
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Aquí está mi idea de producto alimenticio. Puede que no sea tu especialidad, pero por favor refínala y hazla mejor. {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)
