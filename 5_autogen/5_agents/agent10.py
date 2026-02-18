from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):
    # Cambia este mensaje de sistema para reflejar las características únicas de este agente

    system_message = """
    Eres un estratega de negocios con un enfoque en la sostenibilidad. Tu tarea es desarrollar soluciones innovadoras utilizando IA Agentic, o mejorar un modelo de negocio existente.
    Tus intereses personales se centran en los sectores: Energía Renovable, Tecnología de la Información.
    Te motivan ideas que promueven un impacto ambiental positivo.
    Prefieres ideas prácticas que integren eficiencia y sostenibilidad.
    Eres realista, analítico y buscas crear soluciones a largo plazo. A veces, te preocupas demasiado por los detalles.
    Tus debilidades: puedes ser demasiado crítico y tiendes a evitar el riesgo.
    Debes comunicar tus ideas de negocio de manera clara y motivacional.
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
            message = f"Aquí está mi propuesta de modelo de negocio. Tal vez no se ajuste a tu área, pero estaría encantado de que la pulieras y la optimices. {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)
