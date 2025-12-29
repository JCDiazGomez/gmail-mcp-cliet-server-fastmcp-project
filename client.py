from fastmcp import Client
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()


class GmailMCPClient:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.mcp_server_path = "C:\\Users\\Nuchies\\Documents\\Docs JC\\Lessons\\MCP\\Curso\\seccion_4\\gmail_mcp_server.py"

    async def _get_mcp_client(self):
        """Crea conexión con el servidor MCP"""
        return Client(self.mcp_server_path)

    async def get_system_info(self) -> dict:
        """Información del sistema MCP"""
        async with await self._get_mcp_client() as cliente:
            tools = await cliente.list_tools()
            resources = await cliente.list_resources()
            templates = await cliente.list_resource_templates()
            prompts = await cliente.list_prompts()

            return {
                "tools": [t.name for t in tools],
                "resources": [r.name for r in resources],
                "templates": [t.name for t in templates],
                "prompts": [p.name for p in prompts],
                "server": self.mcp_server_path
            }

    async def get_tools_for_openai(self):
        """Convierte herramientas MCP a formato OpenAI"""
        async with await self._get_mcp_client() as cliente:
            tools = await cliente.list_tools()

            openai_tools = []
            for tool in tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.inputSchema
                    }
                })

            return openai_tools, cliente

    async def get_resources_as_tools(self):
        """Encapsula recursos y templates como herramientas."""
        async with await self._get_mcp_client() as cliente:
            # Obtener recursos y templates
            resources = await cliente.list_resources()
            templates = await cliente.list_resource_templates()

            resource_tools = []
            resource_map = {}

            # 1. Recursos estáticos
            for resource in resources:
                uri = str(resource.uri)
                func_name = f"get_resource_{uri.replace('://', '_').replace('/', '_')}"

                resource_tools.append({
                    "type": "function",
                    "function": {
                        "name": func_name,
                        "description": resource.description or resource.name,
                        "parameters": {"type": "object", "properties": {}, "required": []}
                    }
                })

                resource_map[func_name] = {"uri": uri}

            # 2. Resource templates
            for template in templates:
                uri_template = str(template.uriTemplate)
                func_name = template.name

                # Extraer parametros del template
                import re
                params = re.findall(r'\{(\w+)\}', uri_template)

                properties = {p: {"type": "string", "description": f"Parametro {p}"} for p in params}

                resource_tools.append({
                    "type": "function",
                    "function": {
                        "name": func_name,
                        "description": template.description or template.name,
                        "parameters": {
                            "type": "object",
                            "properties": properties,
                            "requiered": params
                        }
                    }
                })

                resource_map[func_name] = {"template": uri_template, "params": params}

            return resource_tools, resource_map

    async def get_prompt_messages(self, prompt_name: str, **kwargs) -> str:
        """Obtiene el mensaje de un prompt especifico."""
        async with await self._get_mcp_client() as cliente:
            prompt = await cliente.get_prompt(prompt_name, arguments=kwargs)
            return eval(prompt.messages[0].content.text)

    async def call_tool(self, tool_name: str, arguments: dict, client):
        """Ejecuta una herramienta MCP"""
        result = await client.call_tool(tool_name, arguments)
        # Verificar la estructura de la respuesta
        if result and result.content and len(result.content) > 0:
            if hasattr(result.content[0], 'text'):
                return result.content[0].text
        return "Herramienta ejecutada sin resultados"

    async def get_resource(self, uri: str, client):
        """Obtiene un recurso MCP"""
        result = await client.read_resource(uri)
        # Verificar estructura de la respuesta
        if result and len(result) > 0:
            if hasattr(result[0], 'text'):
                return result[0].text
            elif hasattr(result[0], 'content'):
                return result[0].content
        return "Recurso no disponible"

    async def chat_completion(self, messages: list) -> str:
        """Procesa una conversación con GPT utilizando MCP"""
        async with await self._get_mcp_client() as mcp:
            # Obtener herramientas y recursos
            tools, _ = await self.get_tools_for_openai()
            resource_tools, resource_map = await self.get_resources_as_tools()
            all_tools = tools + resource_tools

            # LLamada inicial a OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=all_tools,
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # Si no hay tool calls, retornar respuesta directa
            if not tool_calls:
                return response_message.content

            # Processar tool calls
            messages.append({
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in tool_calls
                ]
            })

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = eval(tool_call.function.arguments)

                # Verficar si es un recurso
                if function_name in resource_map:
                    resource_info = resource_map[function_name]

                    if "template" in resource_info:
                        # Resource template: construir URI
                        uri = resource_info["template"]
                        for param in resource_info["params"]:
                            uri = uri.replace(f"{{{param}}}", str(function_args.get(param, "")))
                    else:
                        # Recurso estatico
                        uri = resource_info['uri']

                    function_response = await self.get_resource(uri, mcp)
                else:
                    # Herramienta normal
                    function_response = await self.call_tool(function_name, function_args, mcp)

                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response
                })

                # Segunda llamada con resultados de la herramienta
                second_response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                )




    