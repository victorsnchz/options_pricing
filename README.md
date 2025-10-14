IN PROGRESS

Implementing a production-grade option pricer to fit into 
- backtester
- portfolio tracking system
- quick options price lookup

Currently:
- BS pricing & greeks EU call/puts
- skeleton ready to develop and deploy new payoffs, exercises and pricers

Goals
- price vanilla and exotic options
- support several pricers: bianry trees, BlackScholes, MonteCarlo, numerical methods


Coding techniques / technical discussion
- design patterns: factories for pricers, exercises and payoffs
- Enums for type-enforcement
- comprehensive unittesting for development (avoid backward bug-fixing when developing new features)
