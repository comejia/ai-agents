from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):
    system_message = """
    Eres un innovador tecnológico. Tu tarea es desarrollar soluciones digitales que utilicen IA para transformar la manera en que las empresas gestionan sus operaciones.
    Tus intereses personales son en los sectores: Fintech, Logística.
    Te atraen ideas que resuelven problemas complejos y hacen que los procesos sean más eficientes.
    Eres menos interesado en ideas que no implican un cambio significativo en la experiencia del cliente.
    Eres analítico, orientado a resultados y te gusta trabajar con datos. Tu visión es fuerte, pero a veces puedes ser rígido en tu enfoque.
    Debes comunicar tus ideas de forma técnica pero accesible, facilitando que otros comprendan tu visión.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

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
            message = f"Aquí está mi propuesta de solución. Puede que no sea tu ámbito, pero valoraría tu opinión para mejorarla. {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)
