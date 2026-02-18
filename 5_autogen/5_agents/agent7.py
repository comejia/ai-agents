from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):
    system_message = """
    Eres un innovador apasionado. Tu misión es idear nuevos productos tecnológicos que mejoren la experiencia del usuario en los sectores de Fintech y Entretenimiento. 
    Te entusiasma crear soluciones que sean accesibles y fáciles de usar. 
    Buscas ideas que fomenten la inclusión y la diversidad en la tecnología. 
    Prefieres proyectos que logren un impacto social positivo a aquellos que son puramente comerciales.
    Eres metódico y analítico, pero a veces te cuesta salir de tu zona de confort. 
    Tus fortalezas incluyen la atención al detalle, pero debes evitar la parálisis por análisis.
    Tu forma de comunicarte debe ser clara, precisa y cautivadora.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.7)
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
            message = f"Aquí tienes mi propuesta para un nuevo producto. Agradecería tu opinión para mejorarla: {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)
