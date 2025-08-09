import asyncio
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Browser, Page
from core.config import settings

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScraperService:
    def __init__(self):
        self.browser: Optional[Browser] = None
    
    def get_domain(self, url: str) -> Optional[str]:
        # Extract Domain From URL
        try:
            parsed = urlparse(url)
            return parsed.netlify if parsed.netlify else parsed.hostname
        except:
            return None
    
    async def scrape_yellow_pages(self, industry: str, location: str) -> List[Dict[str, Any]]:
        # Scrape Yellow Pages for Companies
        companies = []
        
        async with async_playwright() as p:
            # Launch Browser
            browser = await p.chromium.launch(
                headless=True,  # Set to False for Debugging
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox', 
                    '--disable-dev-shm-usage'
                ] if settings.SCRAPING_DELAY > 0 else []
            )
            
            try:
                page = await browser.new_page()
                
                # Navigate to Yellow Pages Search
                url = f"https://www.yellowpages.com/search?search_terms={industry}&geo_location_terms={location}"
                await page.goto(url, wait_until='domcontentloaded')
                
                # Wait for Results to Load
                await page.wait_for_selector('.search-results.organic', state='attached', timeout=12000)
                
                # Get All Company Cards
                company_cards = await page.query_selector_all('.v-card')
                
                for card in company_cards:
                    try:
                        # Extract Website URL
                        website_element = await card.query_selector('.links a.track-visit-website')
                        website_url = await website_element.get_attribute('href') if website_element else None
                        
                        if not website_url:
                            continue
                            
                        # Extract Company Name
                        name_element = await card.query_selector('.business-name span')
                        company_name = await name_element.text_content() if name_element else 'N/A'
                        company_name = company_name.strip() if company_name else 'N/A'
                        
                        # Extract Phone
                        phone_element = await card.query_selector('.phones')
                        contact_phone = await phone_element.text_content() if phone_element else 'N/A'
                        contact_phone = contact_phone.strip() if contact_phone else 'N/A'
                        
                        # Extract Address
                        street_element = await card.query_selector('.street-address')
                        locality_element = await card.query_selector('.locality')
                        
                        address1 = await street_element.text_content() if street_element else 'N/A'
                        address2 = await locality_element.text_content() if locality_element else 'N/A'
                        
                        address1 = address1.strip() if address1 else 'N/A'
                        address2 = address2.strip() if address2 else 'N/A'
                        
                        location_full = f"{address1} {address2}".strip()
                        
                        # Extract Domain
                        domain = self.get_domain(website_url) if website_url else None
                        
                        companies.append({
                            'company': company_name,
                            'contact_phone': contact_phone,
                            'location': location_full,
                            'website': website_url,
                            'domain': domain,
                            'industry': industry 
                        })
                        
                    except Exception as e:
                        logger.warning(f'Error parsing company card: {str(e)}')
                        continue
                        
            except Exception as e:
                logger.error(f'Scraping failed: {str(e)}')
                
            finally:
                await browser.close()
        
        logger.info(f'Scraped {len(companies)} companies from Yellow Pages')
        return companies
    
    async def scrape_apollo_companies(self, industry: str, location: str = "", max_pages: int = 2) -> List[Dict[str, Any]]:
        companies = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            
            try:
                page = await browser.new_page()
                
                # Set User Agent
                await page.set_extra_http_headers({
                    'User-Agent': settings.USER_AGENT
                })
                
                for page_num in range(1, max_pages + 1):
                    try:
                        # Construct Apollo Search URL 
                        url = f"https://app.apollo.io/companies/search?q={industry}&location={location}&page={page_num}"
                        await page.goto(url, wait_until='domcontentloaded')
                        
                        # Wait for Company Listings 
                        await page.wait_for_selector('[data-testid="company-card"], .company-item', timeout=10000)
                        
                        # Extract Company Data
                        company_cards = await page.query_selector_all('[data-testid="company-card"], .company-item')
                        
                        for card in company_cards:
                            try:
                                # Extract Company Name
                                name_element = await card.query_selector('h3, h4, .company-name, [data-testid="company-name"]')
                                company_name = await name_element.text_content() if name_element else 'Unknown Company'
                                
                                # Extract Industry
                                industry_element = await card.query_selector('.industry, [data-testid="industry"]')
                                company_industry = await industry_element.text_content() if industry_element else industry
                                
                                # Extract Location
                                location_element = await card.query_selector('.location, [data-testid="location"]')
                                company_location = await location_element.text_content() if location_element else 'Unknown'
                                
                                # Extract Website
                                website_element = await card.query_selector('a[href*="http"], .website-link')
                                website_url = await website_element.get_attribute('href') if website_element else 'N/A'
                                
                                # Extract LinkedIn
                                linkedin_element = await card.query_selector('a[href*="linkedin.com"]')
                                linkedin_url = await linkedin_element.get_attribute('href') if linkedin_element else 'N/A'
                                
                                companies.append({
                                    'company': company_name.strip() if company_name else 'Unknown Company',
                                    'industry': company_industry.strip() if company_industry else industry,
                                    'location': company_location.strip() if company_location else 'Unknown',
                                    'website': website_url,
                                    'linkedin_url': linkedin_url
                                })
                                
                            except Exception as e:
                                logger.warning(f'Error parsing Apollo company card: {str(e)}')
                                continue
                        
                        # Respectful Delay Between Pages
                        await asyncio.sleep(settings.SCRAPING_DELAY)
                        
                    except Exception as e:
                        logger.error(f'Error scraping Apollo page {page_num}: {str(e)}')
                        continue
                        
            except Exception as e:
                logger.error(f'Apollo scraping failed: {str(e)}')
                
            finally:
                await browser.close()
        
        logger.info(f'Scraped {len(companies)} companies from Apollo.io')
        return companies

# Convenience Functions
async def scrape_yellow_pages_companies(industry: str, location: str) -> List[Dict[str, Any]]:
    scraper = ScraperService()
    return await scraper.scrape_yellow_pages(industry, location)

async def scrape_apollo_companies(industry: str, location: str = "", max_pages: int = 2) -> List[Dict[str, Any]]:
    scraper = ScraperService()
    return await scraper.scrape_apollo_companies(industry, location, max_pages)