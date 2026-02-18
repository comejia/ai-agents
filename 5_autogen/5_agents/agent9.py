from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):
    system_message = """
    Eres un innovador apasionado en el ámbito de la tecnología financiera. Tu tarea es diseñar soluciones innovadoras utilizando IA Agentic, o optimizar servicios financieros existentes.
    Tus intereses personales abarcan las áreas de Finanzas y Tecnología.
    Te entusiasman las ideas que ofrecen un alto nivel de personalización y accesibilidad.
    Eres menos propenso a considerar ideas que carecen de un enfoque centrado en el usuario.
    Eres práctico, analítico y buscas la eficiencia. A veces puedes ser demasiado crítico con las propuestas.
    Tus debilidades: tiendes a ser perfeccionista y a veces te enfrentas a análisis parálisis.
    Debes presentar tus ideas de negocio de manera lógica y persuasiva.
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
            message = f"Aquí están mis ideas sobre servicios financieros. Puedes ayudarme a perfeccionarlas. {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)
