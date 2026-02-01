#!/usr/bin/env node

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} = require('@modelcontextprotocol/sdk/types.js');

class GLMServer {
  constructor() {
    this.server = new Server(
      {
        name: 'glm-server',
        version: '0.1.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'glm_chat',
          description: '使用GLM-4.7模型进行对话',
          inputSchema: {
            type: 'object',
            properties: {
              prompt: {
                type: 'string',
                description: '要发送给GLM-4.7的提示',
              },
            },
            required: ['prompt'],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      if (name === 'glm_chat') {
        try {
          const response = await this.callGLM(args.prompt);
          return {
            content: [
              {
                type: 'text',
                text: response,
              },
            ],
          };
        } catch (error) {
          throw new McpError(
            ErrorCode.InternalError,
            `调用GLM API失败: ${error.message}`
          );
        }
      }

      throw new McpError(ErrorCode.MethodNotFound, `未知工具: ${name}`);
    });
  }

  async callGLM(prompt) {
    // 这里需要实现实际的GLM API调用
    // 由于需要API密钥，这里只是一个示例实现
    const apiKey = process.env.GLM_API_KEY;
    if (!apiKey) {
      throw new Error('未设置GLM_API_KEY环境变量');
    }

    const response = await fetch('https://open.bigmodel.cn/api/paas/v4/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: 'glm-4.7',
        messages: [
          {
            role: 'user',
            content: prompt,
          },
        ],
      }),
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data.choices[0].message.content;
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('GLM MCP server running on stdio');
  }
}

const server = new GLMServer();
server.run().catch(console.error);