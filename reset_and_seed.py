#!/usr/bin/env python3
"""
Database reset and reseed script for LLM Development Platform
Drops all tables, recreates them, and seeds with fresh test data
"""

import asyncio
import sys
import uuid
from datetime import datetime
from typing import List, Dict, Any

from app.database import AsyncSessionLocal, init_db, engine, Base
from app.models.organization import Organization
from app.models.user import User
from app.models.project import Project
from app.models.prompt import Prompt, PromptVersion
from app.models.dataset import Dataset, DatasetItem
from app.models.experiment import Experiment, ExperimentRun, ExperimentStatus, RunStatus
from app.models.evaluation import EvaluationResult
from app.models.trace import Trace
from app.models.metrics import EvalMetrics


class DatabaseResetter:
    def __init__(self):
        self.session = None
        self.seeded_data = {}
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = AsyncSessionLocal()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def drop_all_tables(self):
        """Drop all tables in the database"""
        print("🗑️  Dropping all tables...")
        
        try:
            # Drop all tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            
            print("✅ All tables dropped successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to drop tables: {e}")
            return False
    
    async def create_all_tables(self):
        """Create all tables in the database"""
        print("🏗️  Creating all tables...")
        
        try:
            # Create all tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            print("✅ All tables created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create tables: {e}")
            return False
    
    async def seed_organizations(self) -> List[Organization]:
        """Seed organizations"""
        print("🌐 Seeding organizations...")
        
        organizations = [
            Organization(
                name="Acme Corporation",
                slug="acme-corp",
                description="A leading technology company focused on AI and machine learning solutions."
            ),
            Organization(
                name="TechStart Inc",
                slug="techstart",
                description="A startup building innovative AI-powered applications."
            ),
            Organization(
                name="Research Labs",
                slug="research-labs",
                description="Academic research organization specializing in NLP and LLM research."
            )
        ]
        
        for org in organizations:
            self.session.add(org)
        
        await self.session.commit()
        
        # Refresh to get IDs
        for org in organizations:
            await self.session.refresh(org)
        
        print(f"✅ Created {len(organizations)} organizations")
        self.seeded_data['organizations'] = organizations
        return organizations
    
    async def seed_users(self, organizations: List[Organization]) -> List[User]:
        """Seed users"""
        print("👥 Seeding users...")
        
        # Create hashed passwords (in production, use proper password hashing)
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        users = [
            User(
                email="admin@acme.com",
                username="admin_acme",
                hashed_password=pwd_context.hash("password123"),
                full_name="Admin User",
                is_active=True,
                is_superuser=True,
                organization_id=organizations[0].id
            ),
            User(
                email="developer@acme.com",
                username="dev_acme",
                hashed_password=pwd_context.hash("password123"),
                full_name="Developer User",
                is_active=True,
                is_superuser=False,
                organization_id=organizations[0].id
            ),
            User(
                email="founder@techstart.com",
                username="founder_tech",
                hashed_password=pwd_context.hash("password123"),
                full_name="TechStart Founder",
                is_active=True,
                is_superuser=True,
                organization_id=organizations[1].id
            ),
            User(
                email="researcher@research.com",
                username="researcher",
                hashed_password=pwd_context.hash("password123"),
                full_name="Research Scientist",
                is_active=True,
                is_superuser=False,
                organization_id=organizations[2].id
            )
        ]
        
        for user in users:
            self.session.add(user)
        
        await self.session.commit()
        
        # Refresh to get IDs
        for user in users:
            await self.session.refresh(user)
        
        print(f"✅ Created {len(users)} users")
        self.seeded_data['users'] = users
        return users
    
    async def seed_projects(self, organizations: List[Organization], users: List[User]) -> List[Project]:
        """Seed projects"""
        print("📁 Seeding projects...")
        
        projects = [
            Project(
                name="Customer Support AI",
                description="AI-powered customer support system using LLMs to answer customer queries.",
                is_active=True,
                organization_id=organizations[0].id,
                owner_id=users[0].id
            ),
            Project(
                name="Content Generation Platform",
                description="Platform for generating marketing content using various LLM models.",
                is_active=True,
                organization_id=organizations[0].id,
                owner_id=users[1].id
            ),
            Project(
                name="Code Assistant",
                description="AI-powered code completion and review system for developers.",
                is_active=True,
                organization_id=organizations[1].id,
                owner_id=users[2].id
            ),
            Project(
                name="NLP Research",
                description="Research project on natural language processing and model evaluation.",
                is_active=True,
                organization_id=organizations[2].id,
                owner_id=users[3].id
            )
        ]
        
        for project in projects:
            self.session.add(project)
        
        await self.session.commit()
        
        # Refresh to get IDs
        for project in projects:
            await self.session.refresh(project)
        
        print(f"✅ Created {len(projects)} projects")
        self.seeded_data['projects'] = projects
        return projects
    
    async def seed_prompts(self, projects: List[Project]) -> List[Prompt]:
        """Seed prompts and prompt versions"""
        print("💬 Seeding prompts...")
        
        prompts = [
            Prompt(
                name="Customer Support Assistant",
                description="AI assistant for handling customer support queries",
                is_active=True,
                is_deployed=True,
                project_id=projects[0].id
            ),
            Prompt(
                name="Content Writer",
                description="AI writer for generating marketing content",
                is_active=True,
                is_deployed=True,
                project_id=projects[1].id
            ),
            Prompt(
                name="Code Reviewer",
                description="AI code reviewer for analyzing and improving code",
                is_active=True,
                is_deployed=False,
                project_id=projects[2].id
            ),
            Prompt(
                name="Text Summarizer",
                description="AI text summarizer for research papers",
                is_active=True,
                is_deployed=True,
                project_id=projects[3].id
            )
        ]
        
        for prompt in prompts:
            self.session.add(prompt)
        
        await self.session.commit()
        
        # Refresh to get IDs
        for prompt in prompts:
            await self.session.refresh(prompt)
        
        # Create prompt versions
        prompt_versions = [
            PromptVersion(
                version="1.0.0",
                template="You are a helpful customer support assistant. Please help the customer with their query: {{customer_query}}",
                variables={"customer_query": "string"},
                is_deployed=True,
                prompt_id=prompts[0].id
            ),
            PromptVersion(
                version="1.1.0",
                template="You are a helpful customer support assistant. Please help the customer with their query: {{customer_query}}. Be polite and professional.",
                variables={"customer_query": "string"},
                is_deployed=True,
                prompt_id=prompts[0].id
            ),
            PromptVersion(
                version="1.0.0",
                template="You are a professional content writer. Write engaging content about: {{topic}}",
                variables={"topic": "string"},
                is_deployed=True,
                prompt_id=prompts[1].id
            ),
            PromptVersion(
                version="1.0.0",
                template="You are a code reviewer. Review this code and provide feedback: {{code}}",
                variables={"code": "string"},
                is_deployed=False,
                prompt_id=prompts[2].id
            ),
            PromptVersion(
                version="1.0.0",
                template="Summarize the following text in a concise manner: {{text}}",
                variables={"text": "string"},
                is_deployed=True,
                prompt_id=prompts[3].id
            )
        ]
        
        for version in prompt_versions:
            self.session.add(version)
        
        await self.session.commit()
        
        print(f"✅ Created {len(prompts)} prompts with {len(prompt_versions)} versions")
        self.seeded_data['prompts'] = prompts
        self.seeded_data['prompt_versions'] = prompt_versions
        return prompts
    
    async def seed_datasets(self, projects: List[Project]) -> List[Dataset]:
        """Seed datasets and dataset items"""
        print("📊 Seeding datasets...")
        
        datasets = [
            Dataset(
                name="Customer Support Queries",
                description="Collection of customer support queries and expected responses",
                is_active=True,
                project_id=projects[0].id
            ),
            Dataset(
                name="Marketing Content",
                description="Marketing content examples for different industries",
                is_active=True,
                project_id=projects[1].id
            ),
            Dataset(
                name="Code Review Examples",
                description="Code examples for testing code review capabilities",
                is_active=True,
                project_id=projects[2].id
            ),
            Dataset(
                name="Research Papers",
                description="Research paper abstracts for summarization testing",
                is_active=True,
                project_id=projects[3].id
            )
        ]
        
        for dataset in datasets:
            self.session.add(dataset)
        
        await self.session.commit()
        
        # Refresh to get IDs
        for dataset in datasets:
            await self.session.refresh(dataset)
        
        # Create dataset items
        dataset_items = []
        
        # Customer Support Queries
        customer_queries = [
            {"customer_query": "How do I reset my password?"},
            {"customer_query": "I can't log into my account"},
            {"customer_query": "Where can I find my order history?"},
            {"customer_query": "How do I cancel my subscription?"},
            {"customer_query": "What are your business hours?"}
        ]
        
        expected_responses = [
            "To reset your password, go to the login page and click 'Forgot Password'. You'll receive an email with reset instructions.",
            "Please try clearing your browser cache and cookies. If the issue persists, contact our support team.",
            "You can find your order history in your account dashboard under the 'Orders' section.",
            "To cancel your subscription, go to Account Settings > Subscription and click 'Cancel Subscription'.",
            "Our business hours are Monday to Friday, 9 AM to 6 PM EST."
        ]
        
        for i, (query, response) in enumerate(zip(customer_queries, expected_responses)):
            dataset_items.append(DatasetItem(
                input_data=query,
                expected_output=response,
                dataset_id=datasets[0].id
            ))
        
        # Marketing Content
        marketing_topics = [
            {"topic": "AI in healthcare"},
            {"topic": "Sustainable energy solutions"},
            {"topic": "Remote work productivity"},
            {"topic": "Cybersecurity best practices"},
            {"topic": "Digital transformation"}
        ]
        
        for topic in marketing_topics:
            dataset_items.append(DatasetItem(
                input_data=topic,
                expected_output="[Generated marketing content would go here]",
                dataset_id=datasets[1].id
            ))
        
        # Code Review Examples
        code_examples = [
            {"code": "def add(a, b):\n    return a + b"},
            {"code": "for i in range(10):\n    print(i)"},
            {"code": "class User:\n    def __init__(self, name):\n        self.name = name"},
            {"code": "import pandas as pd\ndf = pd.read_csv('data.csv')"},
            {"code": "async def fetch_data():\n    async with aiohttp.ClientSession() as session:\n        async with session.get(url) as response:\n            return await response.json()"}
        ]
        
        for code in code_examples:
            dataset_items.append(DatasetItem(
                input_data=code,
                expected_output="[Code review feedback would go here]",
                dataset_id=datasets[2].id
            ))
        
        # Research Papers
        research_texts = [
            {"text": "This paper presents a novel approach to natural language processing using transformer architectures. The proposed method achieves state-of-the-art results on multiple benchmark datasets."},
            {"text": "We investigate the effectiveness of different machine learning algorithms for sentiment analysis. Our experiments show that deep learning models outperform traditional methods."},
            {"text": "This study examines the impact of data augmentation techniques on model performance. Results indicate significant improvements in accuracy and generalization."},
            {"text": "We propose a new framework for evaluating large language models. The framework provides comprehensive metrics for assessing model capabilities."},
            {"text": "This research explores the relationship between model size and performance in natural language understanding tasks. Findings suggest diminishing returns beyond certain thresholds."}
        ]
        
        for text in research_texts:
            dataset_items.append(DatasetItem(
                input_data=text,
                expected_output="[Generated summary would go here]",
                dataset_id=datasets[3].id
            ))
        
        for item in dataset_items:
            self.session.add(item)
        
        await self.session.commit()
        
        print(f"✅ Created {len(datasets)} datasets with {len(dataset_items)} items")
        self.seeded_data['datasets'] = datasets
        self.seeded_data['dataset_items'] = dataset_items
        return datasets
    
    async def seed_experiments(self, projects: List[Project], prompts: List[Prompt], datasets: List[Dataset]) -> List[Experiment]:
        """Seed experiments and experiment runs"""
        print("🧪 Seeding experiments...")
        
        experiments = [
            Experiment(
                name="Customer Support AI Evaluation",
                description="Evaluating the performance of customer support AI responses",
                status=ExperimentStatus.ACTIVE,
                prompt_id=prompts[0].id,
                dataset_id=datasets[0].id,
                model_configuration={
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.7,
                    "max_tokens": 150
                },
                evaluation_config={
                    "metrics": ["accuracy", "relevance", "helpfulness"],
                    "thresholds": {"accuracy": 0.8, "relevance": 0.7}
                },
                project_id=projects[0].id
            ),
            Experiment(
                name="Content Generation Quality Test",
                description="Testing content generation quality across different topics",
                status=ExperimentStatus.ACTIVE,
                prompt_id=prompts[1].id,
                dataset_id=datasets[1].id,
                model_configuration={
                    "provider": "anthropic",
                    "model": "claude-3-sonnet",
                    "temperature": 0.8,
                    "max_tokens": 200
                },
                evaluation_config={
                    "metrics": ["creativity", "engagement", "clarity"],
                    "thresholds": {"creativity": 0.7, "engagement": 0.6}
                },
                project_id=projects[1].id
            )
        ]
        
        for experiment in experiments:
            self.session.add(experiment)
        
        await self.session.commit()
        
        # Refresh to get IDs
        for experiment in experiments:
            await self.session.refresh(experiment)
        
        # Create experiment runs
        experiment_runs = [
            ExperimentRun(
                id=str(uuid.uuid4()),
                status=RunStatus.COMPLETED,
                total_items=5,
                completed_items=5,
                failed_items=0,
                metrics={"accuracy": 0.85, "relevance": 0.78, "helpfulness": 0.82},
                experiment_id=experiments[0].id,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            ),
            ExperimentRun(
                id=str(uuid.uuid4()),
                status=RunStatus.PENDING,
                total_items=5,
                completed_items=0,
                failed_items=0,
                experiment_id=experiments[1].id
            )
        ]
        
        for run in experiment_runs:
            self.session.add(run)
        
        await self.session.commit()
        
        print(f"✅ Created {len(experiments)} experiments with {len(experiment_runs)} runs")
        self.seeded_data['experiments'] = experiments
        self.seeded_data['experiment_runs'] = experiment_runs
        return experiments
    
    async def seed_sample_traces(self, projects: List[Project], prompts: List[Prompt]) -> List[Trace]:
        """Seed sample traces for testing"""
        print("📈 Seeding sample traces...")
        
        traces = [
            Trace(
                trace_id=f"trace-{uuid.uuid4().hex[:8]}",
                prompt_id=prompts[0].id,
                input_data={"customer_query": "How do I reset my password?"},
                output_data={"response": "To reset your password, go to the login page and click 'Forgot Password'."},
                latency_ms=1250.5,
                tokens_used=45,
                cost_usd=0.0025,
                model_name="gpt-3.5-turbo",
                model_provider="openai",
                is_success=True,
                project_id=projects[0].id
            ),
            Trace(
                trace_id=f"trace-{uuid.uuid4().hex[:8]}",
                prompt_id=prompts[1].id,
                input_data={"topic": "AI in healthcare"},
                output_data={"content": "AI is revolutionizing healthcare by enabling..."},
                latency_ms=2100.0,
                tokens_used=120,
                cost_usd=0.0080,
                model_name="claude-3-sonnet",
                model_provider="anthropic",
                is_success=True,
                project_id=projects[1].id
            )
        ]
        
        for trace in traces:
            self.session.add(trace)
        
        await self.session.commit()
        
        print(f"✅ Created {len(traces)} sample traces")
        self.seeded_data['traces'] = traces
        return traces
    
    async def seed_sample_metrics(self, projects: List[Project]) -> List[EvalMetrics]:
        """Seed sample evaluation metrics"""
        print("📊 Seeding sample metrics...")
        
        import random
        from datetime import datetime, timedelta
        
        metrics = []
        base_time = datetime.utcnow()
        
        for project in projects:
            for i in range(10):  # 10 data points per project
                time_point = base_time - timedelta(hours=i)
                
                metrics.append(EvalMetrics(
                    time=time_point,
                    project_id=project.id,
                    metric_name="accuracy",
                    value=random.uniform(0.7, 0.95)
                ))
                
                metrics.append(EvalMetrics(
                    time=time_point,
                    project_id=project.id,
                    metric_name="latency_ms",
                    value=random.uniform(500, 2000)
                ))
        
        for metric in metrics:
            self.session.add(metric)
        
        await self.session.commit()
        
        print(f"✅ Created {len(metrics)} sample metrics")
        self.seeded_data['metrics'] = metrics
        return metrics
    
    async def reset_and_seed_all(self, skip_reset: bool = False, skip_traces: bool = False, skip_metrics: bool = False):
        """Reset database and seed all data"""
        print("🚀 Starting database reset and seeding...")
        print("=" * 60)
        
        try:
            if not skip_reset:
                # Drop all tables
                if not await self.drop_all_tables():
                    return False
                
                # Create all tables
                if not await self.create_all_tables():
                    return False
            
            # Seed in dependency order
            organizations = await self.seed_organizations()
            users = await self.seed_users(organizations)
            projects = await self.seed_projects(organizations, users)
            prompts = await self.seed_prompts(projects)
            datasets = await self.seed_datasets(projects)
            experiments = await self.seed_experiments(projects, prompts, datasets)
            if not skip_traces:
                traces = await self.seed_sample_traces(projects, prompts)
            if not skip_metrics:
                metrics = await self.seed_sample_metrics(projects)
            
            print("\n" + "=" * 60)
            print("🎉 Database reset and seeding completed successfully!")
            print("=" * 60)
            
            # Print summary
            print("\n📊 Seeded Data Summary:")
            print(f"Organizations: {len(organizations)}")
            print(f"Users: {len(users)}")
            print(f"Projects: {len(projects)}")
            print(f"Prompts: {len(prompts)} (with {len(self.seeded_data['prompt_versions'])} versions)")
            print(f"Datasets: {len(datasets)} (with {len(self.seeded_data['dataset_items'])} items)")
            print(f"Experiments: {len(experiments)} (with {len(self.seeded_data['experiment_runs'])} runs)")
            if not skip_traces:
                print(f"Traces: {len(traces)}")
            if not skip_metrics:
                print(f"Metrics: {len(metrics)}")
            
            print("\n🔑 Test Credentials:")
            for user in users:
                print(f"  {user.email} / password123")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Reset and seeding failed: {e}")
            await self.session.rollback()
            return False


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Reset database and seed with test data")
    parser.add_argument("--skip-reset", action="store_true",
                       help="Skip dropping and recreating tables (just seed data)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without actually doing it")
    parser.add_argument("--force", action="store_true",
                       help="Skip confirmation prompts")
    parser.add_argument("--skip-traces", action="store_true",
                       help="Skip seeding sample traces")
    parser.add_argument("--skip-metrics", action="store_true",
                       help="Skip seeding sample metrics")
    parser.add_argument("--skip-experiments", action="store_true",
                       help="Skip seeding experiments")

    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 Dry run mode - would perform the following:")
        if not args.skip_reset:
            print("- Drop all existing tables")
            print("- Create all tables from scratch")
        print("- Seed 3 organizations")
        print("- Seed 4 users")
        print("- Seed 4 projects")
        print("- Seed 4 prompts with 5 versions")
        print("- Seed 4 datasets with 20 items")
        if not args.skip_experiments:
            print("- Seed 2 experiments with 2 runs")
        if not args.skip_traces:
            print("- Seed 2 sample traces")
        if not args.skip_metrics:
            print("- Seed 40 sample metrics")
        return
    
    if not args.skip_reset and not args.force:
        print("⚠️  WARNING: This will DELETE ALL EXISTING DATA and recreate the database!")
        print("This action cannot be undone.")
        response = input("Are you absolutely sure you want to continue? (type 'yes' to confirm): ")
        if response.lower() != 'yes':
            print("Operation cancelled.")
            return
    
    async with DatabaseResetter() as resetter:
        success = await resetter.reset_and_seed_all(skip_reset=args.skip_reset, skip_traces=args.skip_traces, skip_metrics=args.skip_metrics)
        
        if success:
            print("\n✅ Database reset and seeding completed successfully!")
            print("\n💡 Next steps:")
            print("1. Test database connection: python simple_db_test.py")
            print("2. Test worker functionality: python simple_worker_test.py")
            print("3. Start the API server: python -m uvicorn app.main:app --reload")
            sys.exit(0)
        else:
            print("\n❌ Database reset and seeding failed!")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 