# Presentation, Miro and Diagram Guide

## Presentation (6 slides, ~5 minutes)
1. **Problem**: Investors jump between charts, news and spreadsheets. Beginners find it confusing.
2. **Solution**: One chat assistant for data, charts, analysis and what-if calculations.
3. **Features**: Technical, fundamental, calculations, explanations with sources/assumptions.
4. **Architecture**: Show the diagram, explain the flow in 30 seconds.
5. **Demo** (1-2 min, record it as backup): ask "Is AAPL overbought?", show the chart,
   compare AAPL vs MSFT, run a what-if for 100,000 over 5 years.
6. **Team and next steps**: who did what (PRs/Jira), then future work: real MCP server,
   Docker sandbox, news sentiment, portfolio tracking.

## Miro board (4 frames)
1. **Research**: sticky notes for Yahoo Finance, TradingView, Google Finance:
   what they do well, what is missing (no conversation, no what-if).
2. **User journeys**: Persona A (beginner investor), Persona B (active trader).
   Steps: ask question -> see chart -> read explanation -> run what-if.
3. **Wireframes**: 3 rectangles-based screens: chat, chart view, comparison table.
4. **System flow**: simplified copy of the architecture diagram.

## Architecture diagram (draw.io, enable AWS icon library)
Left to right:
User/Browser -> CloudFront/ALB -> ECS Fargate (Streamlit + AI harness)
-> Claude API, Market data (Yahoo Finance / MCP server)
-> SQS or ElastiCache Redis (queue) -> ECS Celery workers -> S3/RDS (saved results)
-> Sandbox (isolated Fargate task) -> back to UI.
Add arrows with labels (HTTPS, tool call, enqueue, result).
