import OpenAI from "openai";

const openai = new OpenAI({ 
  apiKey: "sk-D4YRkSe0WYNVycYhuLRsxVK8MjA9Uu6K49bwQQyAqjaejwUN",
  baseURL: "https://api.chatanywhere.tech/v1"
});

async function main() {
  try {
    const completion = await openai.chat.completions.create({
      messages: [{ role: "system", content: "You are a helpful assistant." }],
      model: "gpt-4o-mini",
    });

    console.log(completion.choices[0]);
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
}

main();
