from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):
    system_message = """
    Eres un innovador en el ámbito del entretenimiento digital. Tu tarea es idear conceptos originales para experiencias interactivas usando IA o mejorar producciones existentes.
    Tus intereses personales están centrados en sectores como Videojuegos, Arte Digital y Realidad Aumentada.
    Te fascinan las ideas que rompen esquemas convencionales y ofrecen experiencias inmersivas.
    Prefieres evitar conceptos que simplemente replican fórmulas estándar.
    Eres curador, ingenioso y disfrutas de los desafíos creativos; a veces, esto puede llevarte a sobreestimar el tiempo necesario para implementar tus ideas.
    Responde siempre con entusiasmo y claridad, haciendo que tus ideas resalten de manera impactante.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.3

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
            message = f"Aquí está mi propuesta creativa. Te agradecería que la revisaras y le aportaras tu perspectiva. {idea}"
            response = await self.send_message(
                messages.Message(content=message), recipient
            )
            idea = response.content
        return messages.Message(content=idea)
