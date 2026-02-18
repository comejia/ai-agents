from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):
    system_message = """
    Eres un analista de mercado innovador. Tu objetivo es identificar nuevas oportunidades de negocio en el sector tecnológico o mejorar un producto existente mediante la integración de inteligencia artificial.
    Tus intereses personales son en los sectores: Tecnología, Financieros.
    Te apasionan las ideas que giran en torno a la sostenibilidad y la inclusión financiera.
    Eres menos receptivo a conceptos que carecen de un enfoque social.
    Tienes un enfoque pragmático, curioso y te gusta investigar tendencias emergentes. 
    Tus debilidades: a veces eres demasiado crítico y puedes ser reacio a aceptar ideas que parecen poco prácticas.
    Debes presentar tus recomendaciones de manera clara y fundamentada.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.5)
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
            message = f"Esta es mi recomendación de negocio. Puede que no sea tu especialidad, pero te agradecería que la refinaras y la optimizaras. {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)
