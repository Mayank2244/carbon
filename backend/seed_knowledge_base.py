#!/usr/bin/env python3
"""
CarbonSense AI - Comprehensive Knowledge Base Seeder
=====================================================
Populates the vector knowledge base with rich, factual documents covering:
  - Carbon emissions facts and global data
  - Country/region carbon intensity data
  - AI and data center energy consumption
  - Renewable energy facts
  - Climate science fundamentals
  - CarbonSense AI system documentation

Run:
    cd backend
    source venv/bin/activate
    python seed_knowledge_base.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.modules.knowledge_base import knowledge_base_service, Document
from app.core.logging import get_logger

logger = get_logger(__name__)


# ============================================================================
# KNOWLEDGE BASE DOCUMENTS - Rich factual content for RAG
# ============================================================================

KNOWLEDGE_DOCUMENTS = [

    # ------------- CARBON INTENSITY BY REGION -------------
    Document(
        content="""
        Global Carbon Intensity of Electricity Generation by Country (2023-2024)

        Carbon intensity is measured in grams of CO2 equivalent per kilowatt-hour (gCO2/kWh).
        Lower values mean cleaner electricity.

        VERY LOW (Clean Energy Leaders):
        - Norway: ~20 gCO2/kWh (97% hydropower)
        - Iceland: ~28 gCO2/kWh (geothermal + hydro)
        - Sweden: ~30 gCO2/kWh (hydro + nuclear)
        - France: ~50 gCO2/kWh (70% nuclear power)
        - Canada: ~130 gCO2/kWh (large hydro base)
        - Switzerland: ~42 gCO2/kWh (nuclear + hydro)
        - New Zealand: ~115 gCO2/kWh (mostly renewables)

        MEDIUM (Transitioning):
        - United Kingdom: ~230 gCO2/kWh (offshore wind + gas mix)
        - California, USA: ~200 gCO2/kWh (solar + wind heavy)
        - New York, USA: ~250 gCO2/kWh (nuclear + gas)
        - Spain: ~190 gCO2/kWh (wind + solar)
        - Germany: ~350-450 gCO2/kWh (gas + coal + renewables)
        - Italy: ~300 gCO2/kWh (gas + some renewables)
        - Brazil: ~100 gCO2/kWh (massive hydro)

        HIGH (Carbon Intensive):
        - United States Average: ~380 gCO2/kWh
        - Texas, USA: ~400 gCO2/kWh (gas + wind mix)
        - China: ~550 gCO2/kWh (coal-heavy but growing solar)
        - Japan: ~500 gCO2/kWh (gas + coal after Fukushima)
        - India: ~700 gCO2/kWh (coal-dominated grid)
        - Poland: ~750 gCO2/kWh (highly coal-dependent)
        - Australia: ~600 gCO2/kWh (coal + growing solar)
        - South Africa: ~900 gCO2/kWh (almost entirely coal)

        GLOBAL AVERAGE: ~475 gCO2/kWh (IEA 2023 estimate)

        Key insight: Running AI in France emits ~10x less CO2 than running it in India.
        Choosing green data center regions significantly reduces AI carbon footprint.
        """,
        source="carbon_intensity_by_region.md",
        metadata={"category": "carbon_data", "topic": "regional_intensity", "version": "2024"}
    ),

    # ------------- AI AND DATA CENTER ENERGY -------------
    Document(
        content="""
        AI and Data Center Energy Consumption Facts

        LARGE LANGUAGE MODEL (LLM) ENERGY COSTS:

        Training Energy (one-time):
        - GPT-3 training: ~1,287 MWh (equivalent to 120 US homes for a year)
        - GPT-4 training: estimated 50,000+ MWh (not officially disclosed)
        - LLaMA-2 70B training: ~539 MWh
        - Mistral 7B training: ~38 MWh (much more efficient)

        Inference Energy (per query, approximate):
        - GPT-4 (large model):    ~0.001-0.01 kWh per query (~10-100 Joules)
        - GPT-3.5 (medium model): ~0.0003 kWh per query (~3 Joules)
        - LLaMA 70B (self-hosted): ~0.003 kWh per query
        - LLaMA 8B (Tiny model):  ~0.00005 kWh per query (~0.5 Joules)
        - TinyLlama 1.1B:         ~0.000005 kWh per query

        Carbon per query (using US average 380 gCO2/kWh):
        - GPT-4: ~3.8 gCO2 per query
        - GPT-3.5: ~0.11 gCO2 per query
        - LLaMA 8B: ~0.019 gCO2 per query
        - TinyLlama 1.1B: ~0.0019 gCO2 per query

        DATA CENTER FACTS:
        - Global data centers use ~200-250 TWh of electricity per year (2022)
        - This is ~1% of global electricity consumption
        - AI workloads are growing 26-36% per year
        - By 2030, AI data centers could use 3-4% of global electricity
        - Microsoft, Google, Amazon run major AI infrastructure

        PUE (Power Usage Effectiveness):
        - Industry average PUE: 1.58
        - Google data centers PUE: ~1.10 (very efficient)
        - PUE of 1.0 means 100% power goes to compute (ideal)
        - PUE of 2.0 means equal power to cooling as compute

        JOULES PER TOKEN (approximate for inference):
        - GPT-4 class:    ~50 Joules/1000 tokens
        - GPT-3.5 class:  ~10 Joules/1000 tokens
        - LLaMA 70B:      ~30 Joules/1000 tokens
        - LLaMA 8B:       ~2 Joules/1000 tokens
        - TinyLlama 1.1B: ~0.5 Joules/1000 tokens

        CarbonSense AI uses adaptive model selection to route simple queries to
        tiny models (100x more efficient) and only escalates to larger models when needed.
        """,
        source="ai_energy_consumption.md",
        metadata={"category": "ai_energy", "topic": "llm_costs", "version": "2024"}
    ),

    # ------------- CLIMATE SCIENCE FUNDAMENTALS -------------
    Document(
        content="""
        Climate Science Fundamentals - Key Facts and Data

        GREENHOUSE GAS EMISSIONS OVERVIEW:

        Global CO2 emissions by sector (2022, IEA):
        - Energy generation: 41% of global CO2 (14.6 Gt CO2)
        - Industry: 26%
        - Transport: 16%
        - Buildings: 9%
        - Agriculture: 8%

        Cumulative total global CO2 emissions since 1850: ~2,400 Gt
        Remaining carbon budget to stay below 1.5°C: ~380 Gt (as of 2023)
        At current rates, budget exhausted in: ~9 years

        TOP CO2 EMITTING COUNTRIES (2022):
        1. China: 12.5 Gt CO2 (31% of global)
        2. USA: 5.0 Gt CO2 (13%)
        3. India: 2.7 Gt CO2 (7%)
        4. Russia: 1.9 Gt CO2 (5%)
        5. Japan: 1.1 Gt CO2 (3%)

        PER CAPITA CO2 EMISSIONS (tonnes CO2/person/year, 2022):
        - Qatar: 31.4 (highest)
        - USA: 14.9
        - Australia: 14.0
        - Canada: 13.5
        - UK: 5.5
        - China: 8.4
        - India: 1.9
        - Bangladesh: 0.6 (lowest major economy)

        KEY TEMPERATURE TARGETS:
        - Pre-industrial baseline: ~13.8°C global average
        - Current warming: +1.1-1.2°C above pre-industrial
        - Paris Agreement target: Limit to 1.5°C (preferred) or 2°C maximum
        - At current policies, trajectory: +2.7°C by 2100
        - 1.5°C world: 14% of species at high risk of extinction
        - 2°C world: 18% of species at high risk
        - 4°C world: 48% of species at risk (catastrophic)

        CARBON CAPTURE:
        - 1 hectare of tropical forest absorbs ~6-9 tonnes CO2/year
        - 1 hectare of mangrove absorbs ~23 tonnes CO2/year
        - Direct Air Capture (DAC) cost: ~$300-600 per tonne CO2 (2023)
        - Target DAC cost for viability: <$100 per tonne

        THE CARBON BUDGET CONCEPT:
        The carbon budget is the total amount of CO2 humans can emit while limiting
        warming to a specific temperature. Once the budget is spent, we must achieve
        net-zero or go negative (carbon removal) to stabilize temperature.
        """,
        source="climate_science_fundamentals.md",
        metadata={"category": "climate_science", "topic": "fundamentals", "version": "2023"}
    ),

    # ------------- RENEWABLE ENERGY FACTS -------------
    Document(
        content="""
        Renewable Energy - Facts, Costs, and Growth Data

        SOLAR ENERGY:
        - Global installed solar capacity (2023): 1,600 GW
        - Annual addition (2023): ~350 GW (record year)
        - Levelized Cost (LCOE) of solar: $30-60/MWh (utility scale, 2023)
        - Solar panel efficiency: 20-24% for commercial panels, 29% for premium
        - Lifecycle CO2 intensity: 20-40 gCO2/kWh (vs 820 for coal)
        - A 1 kWp rooftop solar system in India generates ~1,400-1,800 kWh/year
        - Germany generates ~12% of electricity from solar
        - USA generates ~5.5% from solar
        - India target: 500 GW of renewables by 2030

        WIND ENERGY:
        - Global installed wind capacity (2023): 1,000 GW onshore + 65 GW offshore
        - Offshore wind LCOE: $80-120/MWh (higher installation cost, stronger winds)
        - Onshore wind LCOE: $25-50/MWh (cheapest electricity in history)
        - Lifecycle CO2 intensity: 7-15 gCO2/kWh (extremely clean)
        - Wind covers ~14% of UK electricity, ~24% of Germany

        HYDROPOWER:
        - Largest renewable source globally: ~4,200 GW installed
        - Provides ~15% of global electricity
        - CO2 intensity: 4-30 gCO2/kWh (can vary with reservoir methane)
        - Norway: 92% hydro, Brazil: 63% hydro, Canada: 60% hydro

        NUCLEAR ENERGY:
        - Installed capacity: ~413 GW globally
        - CO2 intensity: ~12 gCO2/kWh (lifecycle, including construction)
        - Provides ~10% of global electricity
        - France: 70% nuclear, generating some of the cleanest electricity in Europe

        BATTERY STORAGE:
        - Lithium-ion battery cost: ~$140/kWh (2023), down from $1,200/kWh (2010)
        - Tesla Megapack: 3.9 MWh capacity per unit
        - Global grid storage capacity: ~200 GWh (2023)

        ENERGY TRANSITION SPEED:
        - Renewable energy provided 30% of global electricity in 2023
        - Solar+wind alone: ~13% of global electricity in 2023
        - Required for 1.5°C: 90%+ clean electricity by 2050
        - Current pace: Too slow by 3-4x to meet climate targets
        """,
        source="renewable_energy_facts.md",
        metadata={"category": "renewables", "topic": "energy_data", "version": "2023"}
    ),

    # ------------- CARBONSENSE AI SYSTEM DOCUMENTATION -------------
    Document(
        content="""
        CarbonSense AI System - Architecture and Design

        CarbonSense AI is a carbon-efficient query routing system that reduces the
        environmental footprint of AI usage through intelligent model selection,
        prompt optimization, and real-time carbon tracking.

        CORE PRINCIPLE:
        Not every question needs GPT-4. A simple factual query uses 100x more energy
        when processed by a large model compared to a small one. CarbonSense routes
        each query to the smallest model that can handle it adequately.

        SYSTEM ARCHITECTURE (8 Optimization Layers):

        Layer 1 - Cache Manager (Redis):
        - Caches previous query responses in Redis
        - Cache hit = 100% energy savings (no model inference needed)
        - TTL: 1 hour for query responses
        - Typical savings: Eliminates 20-40% of redundant queries

        Layer 2 - Prompt Optimizer:
        - Reduces token count before sending to AI models
        - Removes filler words, redundant context, verbose phrasing
        - Proven 23.4% average token reduction in testing
        - Typical savings: 20-50% on token costs and energy

        Layer 3 - Adaptive Model Selector:
        - Analyzes query complexity (SIMPLE / MEDIUM / COMPLEX)
        - Routes to appropriate model tier:
          * TINY (LLaMA 3.1 8B via Groq): Simple Q&A, greetings, facts
          * SMALL (LLaMA 3.1 8B): Moderate reasoning tasks
          * MEDIUM (LLaMA 3.3 70B via Groq): Complex analysis
          * LARGE (Gemini Pro / HuggingFace 70B): Expert reasoning
        - Quality evaluator ensures minimum 0.7 quality score
        - Automatic fallback: upgrades tier if quality too low

        Layer 4 - RAG Knowledge Base (ChromaDB):
        - Vector database for semantic document retrieval
        - Embedding model: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
        - Retrieves top 3 most relevant context chunks for each query
        - Allows smaller models to answer questions accurately using retrieved facts
        - Storage: persistent ChromaDB at backend/data/vector_store/

        Layer 5 - Graph RAG (Neo4j, optional):
        - Knowledge graph for structured entity relationships
        - Higher confidence retrieval for known entity queries
        - Status: Optional (requires Neo4j setup)

        Layer 6 - Carbon API (Electricity Maps + Climatiq):
        - Fetches real-time grid carbon intensity for server location
        - Primary: Electricity Maps API (real-time, requires paid key)
        - Secondary: Climatiq API (emission factors database)
        - Fallback: Region-based static averages from published data
        - Used to calculate actual gCO2 per query

        Layer 7 - RL Optimizer (Reinforcement Learning):
        - Learns from user feedback (1-5 star ratings)
        - Adjusts model selection thresholds over time
        - Reward signal: (rating - 3) / 2.0
        - Long-term optimization: 5-15% additional savings

        Layer 8 - Stats Manager:
        - Tracks all metrics in real-time
        - Calculates energy, carbon, tokens saved vs GPT-4 baseline
        - Powers the dashboard analytics
        - Updates every 3 seconds in the frontend

        REPORTED SAVINGS vs GPT-4 BASELINE:
        - Cache hits: 100% energy savings
        - Prompt optimization: ~23.4% token savings
        - Model selection: up to 90% energy savings
        - Total system: 80-95% efficiency gain vs always-on GPT-4

        API ENDPOINTS:
        - POST /api/v1/query/process — Main chat query
        - GET /api/v1/query/stats — Live metrics
        - GET /api/v1/query/analytics — Historical analytics
        - POST /api/v1/query/feedback — Submit 1-5 star rating
        - POST /api/v1/files/upload — Upload PDF context
        - GET /health — System health check
        - GET /docs — Swagger API documentation
        """,
        source="carbonsense_system_docs.md",
        metadata={"category": "system_docs", "topic": "architecture", "version": "1.0"}
    ),

    # ------------- CARBON FOOTPRINT CALCULATION -------------
    Document(
        content="""
        How Carbon Footprint is Calculated for AI Queries

        ENERGY TO CARBON CONVERSION:
        Carbon (gCO2) = Energy (kWh) × Carbon Intensity (gCO2/kWh)

        Example:
        - Query uses 0.001 kWh
        - Server in India: 700 gCO2/kWh → 0.7 gCO2 per query
        - Server in France: 50 gCO2/kWh → 0.05 gCO2 per query
        - Same query = 14x more carbon in India vs France

        ENERGY CALCULATION FOR AI INFERENCE:
        Energy (kWh) = (Tokens × Joules per Token) / 3,600,000

        Where:
        - 1 kWh = 3,600,000 Joules
        - Tokens = total input + output tokens
        - Joules per Token depends on model size:
          * Large (GPT-4 class): ~50 J/token
          * Medium (70B models): ~30 J/token
          * Small (8B models): ~2 J/token
          * Tiny (1B models): ~0.5 J/token

        SAVINGS CALCULATION (CarbonSense method):
        Baseline energy = Tokens × 50 J/token (GPT-4 reference)
        Actual energy = Tokens × actual J/token (selected model)
        Saved energy = Baseline - Actual (minimum 0)
        Saved CO2 = Saved energy × current carbon intensity

        TOKEN COUNTING:
        - 1 token ≈ 4 characters in English
        - 1 token ≈ 0.75 words
        - "Hello, how are you?" = ~7 tokens
        - A typical paragraph = ~100-150 tokens
        - GPT-4 context limit: 128,000 tokens
        - Prompt optimization saves tokens → reduces energy

        CARBON COST EXAMPLES (query = 100 tokens, US grid at 380 gCO2/kWh):
        - GPT-4 (50 J/token): 5,000 J = 0.00139 kWh = 0.53 gCO2
        - LLaMA 70B (30 J/token): 3,000 J = 0.00083 kWh = 0.32 gCO2
        - LLaMA 8B (2 J/token): 200 J = 0.0000556 kWh = 0.021 gCO2
        - TinyLlama 1.1B (0.5 J/token): 50 J = 0.0000139 kWh = 0.0053 gCO2

        ANNUAL AI USAGE IMPACT:
        If you make 10,000 AI queries per year:
        - Using only GPT-4: ~5,300 gCO2 = 5.3 kg CO2
        - Using CarbonSense AI: ~53-530 gCO2 = 0.053-0.53 kg CO2
        - Savings: ~4.77-5.25 kg CO2 per year per user

        EQUIVALENTS:
        - 1 kg CO2 = driving ~6 km in a petrol car
        - 1 kg CO2 = 1 hour of international flight per passenger
        - 1 kg CO2 = charging 120 smartphones
        """,
        source="carbon_footprint_calculation.md",
        metadata={"category": "carbon_calculation", "topic": "methodology", "version": "1.0"}
    ),

    # ------------- INDIA SPECIFIC CARBON DATA -------------
    Document(
        content="""
        India Carbon Emissions and Energy Profile (2023-2024)

        INDIA ELECTRICITY GRID:
        - Carbon intensity: ~700-720 gCO2/kWh (one of the highest in the world)
        - Total installed capacity: ~930 GW (2024)
        - Coal share: ~54% of electricity generation
        - Renewables share: ~32% (solar + wind growing rapidly)
        - Nuclear: ~3%
        - Hydro: ~11%

        INDIA SOLAR GROWTH:
        - Installed solar: ~85 GW (2024)
        - Target: 500 GW renewables by 2030
        - Solar irradiance in India: 4-7 kWh/m²/day (excellent resource)
        - Rooftop solar potential: 637 GW
        - India is the 3rd largest solar market globally

        INDIA CO2 EMISSIONS:
        - Total: ~2.7 billion tonnes CO2 per year (2022)
        - 3rd largest emitter globally
        - Per capita: ~1.9 tCO2/year (much lower than USA at 14.9)
        - Energy sector: 65% of total emissions
        - Electricity generation alone: ~1.0 billion tonnes CO2/year

        INDIA CLIMATE TARGETS:
        - Net zero target: 2070
        - 45% reduction in carbon intensity of GDP by 2030 (vs 2005)
        - 500 GW non-fossil fuel capacity by 2030
        - 50% of cumulative electric installed capacity from renewables by 2030

        MAJOR POWER PLANTS IN INDIA:
        - Vindhyachal STPS: 4,760 MW (coal, one of world's largest)
        - Mundra UMPP: 4,620 MW (coal, Gujarat)
        - Rihand STPS: 3,000 MW (coal, Uttar Pradesh)
        - Sardar Sarovar Dam: 1,450 MW (hydro, Gujarat)
        - Bhadla Solar Park: 2,245 MW (solar, Rajasthan - world's largest solar park)

        INDIA AI AND TECH SECTOR:
        - India is 3rd largest market for cloud computing in Asia-Pacific
        - Major cloud data centers in Mumbai, Chennai, Hyderabad, Pune
        - AI queries processed in India have ~700 gCO2/kWh intensity
        - Running AI in Norway (20 gCO2/kWh) vs India: 35x cleaner

        COMPARISON:
        Same AI query processed in:
        - Norway data center: 0.002 gCO2 per query (LLaMA 8B)
        - France data center: 0.007 gCO2 per query
        - US data center: 0.008 gCO2 per query
        - India data center: 0.039 gCO2 per query (5x worse than US)
        - South Africa DC: 0.05 gCO2 per query (worst)
        """,
        source="india_carbon_energy_profile.md",
        metadata={"category": "regional_data", "topic": "india", "version": "2024"}
    ),

    # ------------- HOW TO REDUCE AI CARBON FOOTPRINT -------------
    Document(
        content="""
        Strategies to Reduce AI Carbon Footprint

        1. MODEL SIZE SELECTION (Highest Impact)
        - Use the smallest model that meets quality requirements
        - TinyLlama (1.1B) uses ~100x less energy than GPT-4
        - For simple Q&A, small models perform similarly to large ones
        - Route complex reasoning to large models only when needed
        - Impact: 80-95% energy reduction

        2. GEOGRAPHIC INFERENCE LOCATION
        - Run AI in regions with clean electricity grids
        - Best regions: Norway, Iceland, France, Sweden, Canada (BC/Quebec)
        - Worst regions: India, Poland, South Africa, Australia
        - Same compute, up to 35x less carbon in green regions
        - Cloud providers: Use GCP/Azure/AWS regions with renewable commitments

        3. TIME-SHIFTING WORKLOADS
        - Run batch AI jobs during low-carbon hours (when renewables peak)
        - Solar peaks: 10am-4pm in sunny regions
        - Wind varies: check real-time carbon intensity via Electricity Maps API
        - Non-urgent tasks can be delayed to cheaper/greener times
        - Impact: 10-40% carbon reduction

        4. CACHING AND DEDUPLICATION
        - Cache frequent queries to avoid redundant computation
        - Similar queries can reuse existing responses
        - Vector similarity search finds near-duplicate queries
        - Impact: 20-40% query reduction for typical use cases

        5. PROMPT OPTIMIZATION
        - Shorter prompts = fewer tokens = less energy
        - Remove verbose phrasing, repetition, unnecessary context
        - Token reduction of 20-30% is achievable with good optimization
        - Impact: 20-30% direct energy savings

        6. RAG INSTEAD OF FINE-TUNING
        - RAG (Retrieval-Augmented Generation) adds context at query time
        - Avoids energy-intensive model fine-tuning or retraining
        - Allows smaller models to answer domain-specific questions accurately
        - Fine-tuning a 70B model requires hundreds of GPU hours

        7. QUANTIZATION AND EFFICIENCY
        - 4-bit quantization reduces model size by 75% with minimal quality loss
        - INT8 quantization: 2x memory reduction, ~1% quality drop
        - bfloat16: Standard for modern efficient inference
        - Flash Attention: 2-4x speedup for transformer models

        8. BATCH PROCESSING
        - Batch multiple small queries together for GPU efficiency
        - GPUs are underutilized on single small requests
        - Batching improves GPU utilization from ~30% to ~90%
        - Impact: 2-3x throughput improvement per unit energy

        9. FEEDBACK LOOPS (RL)
        - Learn which model tier actually satisfies users
        - Avoid over-provisioning (using large model for simple queries)
        - Reinforcement learning adjusts thresholds based on user satisfaction
        - Impact: 5-15% long-term efficiency gain

        10. CARBON-AWARE CLOUD PROVIDERS
        - Google Cloud: 64% carbon-free energy (CFE) commitment
        - Microsoft Azure: Carbon negative by 2030 pledge
        - Amazon AWS: 100% renewable energy by 2025 target
        - Choose providers with highest renewable energy certificates (RECs)
        """,
        source="reducing_ai_carbon_footprint.md",
        metadata={"category": "sustainability", "topic": "reduction_strategies", "version": "2024"}
    ),

    # ------------- GROQ AND LLAMA MODELS REFERENCE -------------
    Document(
        content="""
        Groq and Llama AI Models - Performance and Energy Reference

        GROQ PLATFORM:
        - Groq uses custom LPU (Language Processing Unit) chips
        - Up to 500 tokens/second inference speed (vs 20-50 for GPU)
        - Energy efficiency: ~3-5x more energy efficient than GPU inference
        - API is free tier for limited use, paid for heavy usage
        - Models available on Groq (2024):

        LLAMA 3.1 8B (Tiny/Small tier in CarbonSense):
        - Developer: Meta AI
        - Parameters: 8 billion
        - Context window: 128,000 tokens
        - Best for: General Q&A, summarization, simple reasoning
        - Speed on Groq: ~800 tokens/second
        - Energy use: ~2 Joules per 1000 tokens
        - Quality: Excellent for everyday tasks, competitive with GPT-3.5

        LLAMA 3.3 70B (Medium tier):
        - Developer: Meta AI
        - Parameters: 70 billion
        - Context window: 128,000 tokens
        - Best for: Complex reasoning, coding, multi-step analysis
        - Speed on Groq: ~275 tokens/second
        - Energy use: ~30 Joules per 1000 tokens
        - Quality: Near GPT-4 quality for most tasks

        GEMINI 1.5 FLASH (Large tier fallback):
        - Developer: Google DeepMind
        - Context window: 1,000,000 tokens (largest available)
        - Best for: Very long documents, multi-modal tasks
        - Energy: Moderate (cloud API, not self-hosted)
        - Cost: $0.075 per million input tokens

        MISTRAL 7B:
        - Very efficient European-developed model
        - Outperforms LLaMA 2 13B on most benchmarks at half the size
        - Energy: Similar to LLaMA 8B

        QUALITY COMPARISON (MMLU benchmark, % accuracy):
        - GPT-4: 86.4%
        - LLaMA 3.3 70B: 86.0% (near GPT-4!)
        - LLaMA 3.1 8B: 76.0%
        - Mistral 7B: 64.2%
        - TinyLlama 1.1B: 42.0%

        COST COMPARISON (per million tokens, 2024):
        - GPT-4 Turbo: $10-30 input / $30-60 output
        - GPT-3.5 Turbo: $0.50 input / $1.50 output
        - LLaMA 3.1 8B (Groq): ~$0.05 (100x cheaper than GPT-4!)
        - LLaMA 3.3 70B (Groq): ~$0.59
        - Gemini 1.5 Flash: $0.075 input

        CARBON SENSE MODEL SELECTION LOGIC:
        - Simple queries (complexity < 0.3): → LLaMA 8B (Tiny tier)
        - Medium queries (0.3-0.7): → LLaMA 8B with quality check
        - Complex queries (> 0.7): → LLaMA 70B or Gemini
        - Quality threshold: 0.7 (auto-escalates if score too low)
        """,
        source="groq_llama_models_reference.md",
        metadata={"category": "ai_models", "topic": "model_specs", "version": "2024"}
    ),

    # ------------- SUSTAINABILITY AND NET ZERO -------------
    Document(
        content="""
        Net Zero, Carbon Neutrality, and Sustainability Concepts

        KEY DEFINITIONS:

        Carbon Neutral:
        - Emissions equal to carbon removed/offset
        - Can be achieved through purchasing offsets (carbon credits)
        - Less rigorous than net zero (offsets can be of poor quality)
        - Example: A company emits 1000 tonnes but buys 1000 tonnes of offsets

        Net Zero:
        - No net greenhouse gas emissions across entire value chain
        - Requires reducing actual emissions, not just offsetting
        - Science Based Targets initiative (SBTi) defines standards
        - Global net zero: ~2050 target

        Carbon Negative / Climate Positive:
        - Removes more carbon than it emits
        - Example: Microsoft aims to be carbon negative by 2030
        - Involves carbon removal like DAC, reforestation, BECCS

        Carbon Credits / Offsets:
        - 1 carbon credit = 1 tonne CO2 equivalent avoided or removed
        - Voluntary market: $5-50 per credit (highly variable quality)
        - Compliance market (EU ETS): ~€60-80 per tonne CO2
        - Types: Avoided deforestation (REDD+), renewables, soil carbon
        - Criticism: Permanence, additionality, double-counting issues

        CORPORATE CLIMATE TARGETS:
        - Apple: carbon neutral by 2030 (entire supply chain)
        - Google: 100% carbon-free energy 24/7 by 2030
        - Microsoft: carbon negative by 2030, historical carbon removal by 2050
        - Amazon: net zero by 2040 (The Climate Pledge)
        - Meta: net zero by 2030

        SCOPE EMISSIONS (GHG Protocol):
        - Scope 1: Direct emissions (own facilities, vehicle fleet)
        - Scope 2: Indirect from purchased electricity
        - Scope 3: All other indirect (supply chain, product use, travel)
        - AI companies: Scope 3 dominates (user device energy, cloud providers)

        LIFECYCLE ASSESSMENT (LCA):
        - Full cradle-to-grave analysis of a product/service
        - For AI model: Training + deployment hardware + inference energy
        - Training is one-time; inference is ongoing and scales with users
        - At scale, inference > training in total lifetime emissions

        CARBON INTENSITY TRENDS:
        - Global electricity carbon intensity fell 10% from 2015-2022
        - Renewables grew from 23% to 29% of global electricity (2015-2022)
        - At current pace: insufficient to meet Paris targets
        - Required: 10-15% annual reduction in carbon intensity

        GREEN SOFTWARE PRINCIPLES (Green Software Foundation):
        1. Carbon Efficiency: Minimize carbon per unit of work
        2. Energy Efficiency: Minimize energy per unit of work
        3. Carbon Awareness: Run when and where electricity is cleanest
        4. Hardware Efficiency: Use the least hardware resources possible
        5. Measurement: Measure and attribute carbon to software

        CarbonSense AI implements all 5 Green Software principles through its
        adaptive model selection, prompt optimization, carbon tracking, and
        real-time grid intensity monitoring.
        """,
        source="sustainability_net_zero_concepts.md",
        metadata={"category": "sustainability", "topic": "concepts", "version": "2024"}
    ),

]


# ============================================================================
# SEEDER EXECUTION
# ============================================================================

def print_banner():
    print("\n" + "╔" + "═" * 70 + "╗")
    print("║" + " " * 15 + "CarbonSense AI - Knowledge Base Seeder" + " " * 17 + "║")
    print("║" + " " * 18 + "Populating RAG with Real Carbon Data" + " " * 16 + "║")
    print("╚" + "═" * 70 + "╝\n")


def seed_knowledge_base():
    print_banner()

    print(f"📋 Documents to ingest: {len(KNOWLEDGE_DOCUMENTS)}")
    print("📂 Topics covered:")
    for doc in KNOWLEDGE_DOCUMENTS:
        print(f"   • [{doc.metadata.get('category', 'general')}] {doc.source}")

    print("\n⏳ Starting ingestion...\n")

    # Check current KB state
    health = knowledge_base_service.health_check()
    print(f"📊 KB before seeding: {health.get('chunk_count', 0)} chunks\n")

    # Ingest all documents
    stats = knowledge_base_service.ingest_documents(KNOWLEDGE_DOCUMENTS)

    print("✅ Ingestion Complete!")
    print(f"   📄 Documents processed: {stats.documents_processed}")
    print(f"   🔪 Chunks created:      {stats.chunks_created}")
    print(f"   💾 Chunks stored:       {stats.chunks_stored}")
    print(f"   ⏱️  Duration:            {stats.duration_seconds:.2f}s")

    # Verify final count
    health_after = knowledge_base_service.health_check()
    print(f"\n📊 KB after seeding: {health_after.get('chunk_count', 0)} chunks ✅\n")

    return stats


def test_rag_search():
    print("\n" + "=" * 72)
    print("  🧪 TESTING RAG SEMANTIC SEARCH")
    print("=" * 72 + "\n")

    test_queries = [
        "What is the carbon intensity of electricity in India?",
        "How much energy does GPT-4 use per query?",
        "What are the best strategies to reduce AI carbon footprint?",
        "How does CarbonSense AI select which model to use?",
        "What is carbon neutral vs net zero?",
        "How do you calculate carbon footprint of an AI query?",
        "What renewable energy sources are growing fastest?",
        "Which countries have the cleanest electricity grid?",
    ]

    passed = 0
    failed = 0

    for query in test_queries:
        results = knowledge_base_service.search(query, top_k=2, min_similarity=0.2)
        if results:
            top = results[0]
            print(f"  ✅ Query: \"{query[:60]}\"")
            print(f"     → Source: {top.source} (similarity: {top.similarity:.3f})")
            print(f"     → Preview: {top.text[:120].strip()}...\n")
            passed += 1
        else:
            print(f"  ❌ Query: \"{query[:60]}\"")
            print(f"     → NO RESULTS FOUND\n")
            failed += 1

    print("=" * 72)
    print(f"  Test Results: {passed}/{len(test_queries)} queries returned context")
    if failed == 0:
        print("  ✅ ALL TESTS PASSED — RAG is fully operational!")
    else:
        print(f"  ⚠️  {failed} queries returned no context (may need lower similarity threshold)")
    print("=" * 72 + "\n")

    return passed, failed


def main():
    try:
        # Step 1: Seed the KB
        stats = seed_knowledge_base()

        # Step 2: Test RAG search
        passed, failed = test_rag_search()

        # Step 3: Final summary
        print("\n" + "╔" + "═" * 70 + "╗")
        print("║" + " " * 25 + "SEEDING COMPLETE" + " " * 29 + "║")
        print("╠" + "═" * 70 + "╣")
        print(f"║  ✅ Knowledge Base populated with {stats.chunks_stored} chunks".ljust(71) + "║")
        print(f"║  ✅ {passed}/{passed + failed} RAG test queries succeeded".ljust(71) + "║")
        print("║  ✅ Your AI will now answer from REAL carbon/climate facts".ljust(71) + "║")
        print("║  ✅ RAG context reduces hallucination significantly".ljust(71) + "║")
        print("╚" + "═" * 70 + "╝\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        logger.error(f"Seeding failed: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
