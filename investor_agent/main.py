"""
Помощник инвестора в Свердловской области
Главный файл запуска агента
"""
import asyncio
import sys
import os

# Настройка кодировки для Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')
import json
from pathlib import Path
from loguru import logger

from src.agent import InvestorAgent
from config import REGION


async def demo_investor_agent():
    """
    Демонстрация возможностей агента
    """
    print("=" * 60)
    print(f"🏭 Помощник инвестора в Свердловской области")
    print("=" * 60)
    print()
    
    async with InvestorAgent() as agent:
        # ==================== 1. ПОИСК ЛУЧШИХ ПРАКТИК ====================
        print("📊 1. Поиск лучших отраслевых практик")
        print("-" * 40)
        
        practices = await agent.find_best_practices(industry="металлургия")
        
        for i, practice in enumerate(practices[:3], 1):
            print(f"\n  {i}. {practice.practice.name}")
            print(f"     Регион: {practice.practice.region}")
            print(f"     Применимость: {practice.applicability_score:.1%}")
            print(f"     Результаты: {practice.practice.results}")
            print(f"     Рекомендации:")
            for rec in practice.adaptation_recommendations[:2]:
                print(f"       • {rec}")
        
        print()
        
        # ==================== 2. ИНВЕСТИЦИОННЫЕ ВОЗМОЖНОСТИ ====================
        print("💰 2. Поиск инвестиционных возможностей")
        print("-" * 40)
        
        opportunities = await agent.find_investment_opportunities(
            industry="металлургия",
            min_investment=10_000_000
        )
        
        for i, opp in enumerate(opportunities[:3], 1):
            print(f"\n  {i}. {opp.title}")
            print(f"     Тип: {opp.type}")
            print(f"     Локация: {opp.location}")
            print(f"     Инвестиции: {opp.investment_required:,.0f} руб.")
            print(f"     Статус: {opp.status}")
        
        print()
        
        # ==================== 3. МЕРЫ ПОДДЕРЖКИ ====================
        print("📋 3. Меры государственной поддержки")
        print("-" * 40)
        
        measures = await agent.find_support_measures(
            industry="металлургия",
            business_size="medium"
        )
        
        for i, measure in enumerate(measures, 1):
            print(f"\n  {i}. {measure.name}")
            print(f"     Тип: {measure.type}")
            print(f"     Сумма: до {measure.max_amount:,.0f} руб.")
            print(f"     Срок подачи: {measure.deadline or 'Нет ограничений'}")
            print(f"     Документы: {len(measure.documents_required)} поз.")
        
        print()
        
        # ==================== 4. ИНВЕСТПРЕДЛОЖЕНИЕ ====================
        if opportunities:
            print("📈 4. Формирование инвестиционного предложения")
            print("-" * 40)
            
            proposal = await agent.create_investment_proposal(
                opportunity=opportunities[0],
                industry="металлургия"
            )
            
            print(f"\n  Предложение: {proposal.title}")
            print(f"  Общие инвестиции: {proposal.total_investment:,.0f} руб.")
            print(f"  Собственные средства: {proposal.own_funds_required:,.0f} руб.")
            print(f"  Доступная поддержка: {proposal.support_funds_available:,.0f} руб.")
            print(f"  Окупаемость: {proposal.payback_period:.1f} лет")
            print(f"  ROI: {proposal.roi:.1f}% годовых")
            
            print(f"\n  Этапы реализации:")
            for stage in proposal.implementation_plan[:2]:
                print(f"    • Этап {stage['stage']}: {stage['name']} ({stage['duration']})")
            
            print(f"\n  Рекомендации:")
            for rec in proposal.recommendations[:3]:
                print(f"    • {rec}")
            
            print()
        
        # ==================== 5. ПОДГОТОВКА ДОКУМЕНТОВ ====================
        print("📄 5. Подготовка пакета документов")
        print("-" * 40)
        
        # Создание шаблонов
        agent.documents.create_template_files()
        
        # Данные проекта
        project_data = {
            "applicant_name": "ООО 'Уральский завод'",
            "inn": "6601000001",
            "ogrn": "1026600000001",
            "address": "г. Екатеринбург, ул. Примерная, 1",
            "contact_phone": "+7 (343) 000-00-00",
            "contact_email": "info@uralzavod.ru",
            "project_name": "Расширение производства металлоконструкций",
            "industry": "металлургия",
            "description": "Модернизация производственной линии и увеличение мощности",
            "investment_amount": 100_000_000,
            "grant_amount": 30_000_000,
            "jobs_created": 75,
            "implementation_period": 18,
            "justification": "Проект соответствует приоритетам развития региона",
            "expected_results": "Рост выпуска продукции на 40%, создание 75 рабочих мест"
        }
        
        # Создание пакета документов
        package = await agent.prepare_documents_package(
            measure_name="Грант на развитие промышленного производства",
            measure_type="grant",
            project_data=project_data
        )
        
        print(f"\n  Пакет документов: {package.id}")
        print(f"  Мера: {package.measure_name}")
        print(f"  Статус: {package.status}")
        print(f"\n  Документы в пакете:")
        for doc in package.documents:
            status_icon = "✅" if doc["status"] == "generated" else "❌"
            print(f"    {status_icon} {doc['type']}: {doc['filename']}")
        
        # Верификация
        print(f"\n  Верификация документов:")
        verification = await agent.verify_documents(package)
        
        print(f"    Общий статус: {'✅ Готово' if verification['overall_valid'] else '⚠️ Требует доработки'}")
        
        if verification['recommendations']:
            print(f"    Рекомендации:")
            for rec in verification['recommendations'][:3]:
                print(f"      • {rec}")
        
        print()
        
        # ==================== 6. ЧЕК-ЛИСТ ====================
        print("✓ 6. Чек-лист документов для гранта")
        print("-" * 40)
        
        checklist = agent.get_documents_checklist("grant")
        for item in checklist:
            print(f"  {item}")
        
        print()
        
        # ==================== 7. КОМПЛЕКСНЫЙ АНАЛИЗ ====================
        print("📊 7. Комплексный анализ отрасли")
        print("-" * 40)
        
        full_analysis = await agent.full_investment_analysis(
            industry="металлургия",
            min_investment=50_000_000
        )
        
        print(f"\n  Отрасль: {full_analysis['industry']}")
        print(f"  Регион: {full_analysis['region']}")
        print(f"\n  Найдено:")
        print(f"    • Лучших практик: {len(full_analysis['sections']['best_practices'])}")
        print(f"    • Инвестплощадок: {len(full_analysis['sections']['opportunities'])}")
        print(f"    • Мер поддержки: {len(full_analysis['sections']['support_measures'])}")
        
        print(f"\n  Ключевые рекомендации:")
        for rec in full_analysis['sections']['recommendations']:
            print(f"    • {rec}")
        
        print()
        print("=" * 60)
        print("✅ Демонстрация завершена!")
        print("=" * 60)
        
        # Сохранение отчёта
        report_path = Path("output/reports/full_analysis.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(full_analysis, ensure_ascii=False, indent=2, default=str),
            encoding='utf-8'
        )
        print(f"\n📁 Полный отчёт сохранён: {report_path}")
        
        return full_analysis


def main():
    """Точка входа"""
    logger.info("Запуск Помощника инвестора")
    
    print()
    print(f"Регион: {REGION['name']}")
    print(f"Столица: {REGION.get('capital', 'Н/Д')}")
    print()
    
    # Запуск демонстрации
    result = asyncio.run(demo_investor_agent())
    
    return result


if __name__ == "__main__":
    main()
