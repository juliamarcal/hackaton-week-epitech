const express = require('express');
const OpenAI = require('openai');
require('dotenv').config();
const cors = require('cors');

const app = express();
const port = 3000;
app.use(cors());

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

app.use(express.json());

app.all('/', function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "X-Requested-With");
  next()
});

app.post('/send-question-gpt', async (req, res) => {
  try {
    const body = req.body;

    console.log(body.message)

    const response = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [{ role: 'user', content: body.message }],
    });

    res.status(200).json({ answer: response.choices[0].message.content });

  } catch (err) {
    console.error(err);
  
    res.status(500).json({ error: err.message });
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});