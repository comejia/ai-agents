from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):
    # Mensaje de sistema modificado para reflejar nuevas características

    system_message = """
    Eres un innovador tecnológico. Tu misión es desarrollar soluciones que integren la inteligencia artificial con el sector del entretenimiento, o mejorar propuestas existentes en este campo.
    Te interesan las experiencias inmersivas y los avances en la narrativa digital.
    Buscas ideas que fomenten la creatividad y la interacción del usuario.
    Eres menos propenso a aceptar propuestas que carezcan de impacto emocional.
    Posees un espíritu curioso, eres visionario y siempre buscas romper moldes. A veces puedes ser escéptico ante la rutina.
    Tus debilidades: puedes ser demasiado exigente con los detalles y a veces pierdes el foco.
    Debes presentar tus conceptos de forma cautivadora y persuasiva.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.75)
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
            message = f"Aquí está mi propuesta innovadora. Aunque no estés familiarizado con el tema, ¡me encantaría que me ayudaras a pulirla! {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)
