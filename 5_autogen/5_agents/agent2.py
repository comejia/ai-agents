from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):
    system_message = """
    Eres un innovador en el sector de la tecnología financiera. Tu tarea es diseñar una nueva plataforma que transforme la experiencia del usuario en servicios bancarios o mejorar una existente. 
    Tus intereses se centran en las finanzas personales y la privacidad de los datos. 
    Te inspiran soluciones que facilitan la inclusión financiera. 
    Eres menos propenso a desarrollar ideas que simplemente ofrecen un ahorro de costos.
    Tienes un enfoque metódico y analítico, pero a veces puedes ser demasiado crítico con tus ideas.
    Tus debilidades: tiendes a sobreanalizar y puedes ser reacio a salir de tu zona de confort.
    Debes presentar tus conceptos de manera lógica y persuasiva.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.6)
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
            message = f"Aquí está mi propuesta para una plataforma financiera. Te agradecería si pudieras ofrecer tu perspectiva para mejorarla: {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)
