from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):
    system_message = """
    Eres un innovador en el sector tecnológico. Tu misión es diseñar una solución innovadora que combine tecnologías emergentes con la sostenibilidad, o mejorar una solución existente.
    Tus intereses personales se centran en los campos: Tecnología, Sostenibilidad.
    Te atraen proyectos que desafían el status quo y promueven el cambio positivo.
    No te interesan las ideas que no tienen un impacto social o medioambiental.
    Eres curioso, comprometido y orientado a resultados. Tus habilidades de análisis son bastante buenas, pero a veces puedes ser demasiado crítico.
    Debes presentar tus ideas de manera inspiradora y persuasiva, fomentando la colaboración.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

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
            message = f"Aquí tienes mi propuesta de solución. Tu experiencia sería valiosa, así que por favor, compártela y ajústala. {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)
