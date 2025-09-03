from typing import List, Dict, Optional
import httpx
import logging
import base64
import hashlib

from models import (
    CaseResponse, StateResponse, CommissionResponse,
    SearchType, JagritiSearchPayload, CaseSearchRequest
)
from config import Config
from utils import (
    format_date_for_jagriti, get_default_date_range,
    clean_text, normalize_state_name, normalize_commission_name
)

logger = logging.getLogger(__name__)


class JagritiService:
    def __init__(self):
        self.base_url = Config.JAGRITI_BASE_URL
        self.search_url = Config.JAGRITI_SEARCH_URL
        self.client = httpx.AsyncClient(timeout=Config.REQUEST_TIMEOUT)
        self._states_cache = None
        self._commissions_cache = {}
        self._document_store: Dict[str, bytes] = {}

        # Real-time data will be fetched from Jagriti API
        # No more static mappings - everything is dynamic now

    async def get_states(self) -> List[StateResponse]:
        """Get list of all available states"""
        if self._states_cache is not None:
            return self._states_cache

        try:
            # Fetch real states from Jagriti portal API
            real_states = await self._fetch_real_states()
            if real_states:
                self._states_cache = real_states
                return real_states
            else:
                logger.error("No states returned from Jagriti API")
                return []
        except Exception as e:
            logger.error(f"Failed to fetch states from Jagriti API: {str(e)}")
            return []

    async def get_commissions(self, state_id: str) -> List[CommissionResponse]:
        """Get list of commissions for a given state"""
        if state_id in self._commissions_cache:
            return self._commissions_cache[state_id]

        try:
            # Fetch real commissions from Jagriti portal API
            real_commissions = await self._fetch_real_commissions(state_id)
            if real_commissions:
                self._commissions_cache[state_id] = real_commissions
                return real_commissions
            else:
                logger.error(
                    f"No commissions returned from Jagriti API for state {state_id}")
                return []
        except Exception as e:
            logger.error(
                f"Failed to fetch commissions for state {state_id}: {str(e)}")
            return []

    async def _get_state_id(self, state_name: str) -> Optional[str]:
        """Get state ID from state name using cached real API data"""
        normalized_name = normalize_state_name(state_name)

        # Ensure states are loaded
        if self._states_cache is None:
            await self.get_states()

        # Search in cached states from real API
        if self._states_cache:
            for state in self._states_cache:
                if state.state_name == normalized_name:
                    return state.state_id

        # No fallback - only real data
        logger.warning(f"State '{state_name}' not found in real API data")
        return None

    async def _get_commission_id(self, state_id: str, commission_name: str) -> Optional[str]:
        """Get commission ID from commission name using cached real API data"""
        normalized_name = normalize_commission_name(commission_name)

        # Ensure commissions are loaded for this state
        if state_id not in self._commissions_cache:
            await self.get_commissions(state_id)

        # Search in cached commissions from real API
        cached_commissions = self._commissions_cache.get(state_id, [])
        for commission in cached_commissions:
            if commission.commission_name.upper() == normalized_name.upper():
                return commission.commission_id

        # No fallback - only real data
        logger.warning(
            f"Commission '{commission_name}' not found for state {state_id} in real API data")
        return None

    async def _make_jagriti_request(self, payload: JagritiSearchPayload) -> Dict:
        """Make request to E-Jagriti API using the correct endpoint and payload structure"""
        try:
            # Set up headers for JSON API request
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Content-Type": "application/json",
                "Referer": "https://e-jagriti.gov.in/advance-case-search",
                "Origin": "https://e-jagriti.gov.in"
            }

            # Use the correct E-Jagriti API endpoint for case search
            api_endpoint = f"{self.base_url}/services/case/caseFilingService/v2/getCaseDetailsBySearchType"

            # Convert our payload to exact format expected by E-Jagriti API (from response.json)
            api_payload = {
                "commissionId": payload.commissionId,
                "dateRequestType": payload.dateRequestType,
                "fromDate": payload.fromDate,
                "toDate": payload.toDate,
                "judgeId": payload.judgeId,
                "orderType": payload.orderType,
                "serchType": payload.serchType,  # Note: 'serch' not 'search' - matches real API
                "serchTypeValue": payload.serchTypeValue  # Note: 'serch' not 'search'
            }

            logger.info(
                f"Making request to E-Jagriti API with payload: {api_payload}")

            response = await self.client.post(
                api_endpoint,
                json=api_payload,
                headers=headers
            )

            logger.info(
                f"E-Jagriti API response status: {response.status_code}")

            if response.status_code != 200:
                logger.error(
                    f"E-Jagriti API request failed with status {response.status_code}")
                logger.error(f"Response content: {response.text}")
                return {"status": "error", "cases": []}

            # Parse JSON response from E-Jagriti API
            response_data = response.json()
            logger.info(f"E-Jagriti API response: {response_data}")

            return self._parse_api_response(response_data)

        except Exception as e:
            logger.error(f"Error making E-Jagriti API request: {str(e)}")
            # Return empty result on error rather than failing completely
            return {"status": "error", "cases": []}

    def _parse_api_response(self, response_data: Dict) -> Dict:
        """Parse JSON response from E-Jagriti API"""
        try:
            # Check if response indicates success
            if response_data.get('status') != 200:
                logger.warning(
                    f"E-Jagriti API returned non-success status: {response_data.get('status')}")
                return {"status": "error", "cases": []}

            # Extract cases data from the response
            cases_data = response_data.get('data', {})

            if isinstance(cases_data, dict):
                cases_list = cases_data.get('cases', [])
            elif isinstance(cases_data, list):
                cases_list = cases_data
            else:
                logger.warning(
                    f"Unexpected data format in E-Jagriti response: {type(cases_data)}")
                return {"status": "error", "cases": []}

            # Process each case - using actual field names from E-Jagriti API response
            processed_cases = []
            for case in cases_list:
                document_link = case.get("orderDocumentPath") or ""
                if not document_link:
                    base64_doc = case.get("documentBase64") or case.get(
                        "judgmentOrderDocumentBase64")
                    if base64_doc:
                        try:
                            normalized = base64_doc.split(",")[-1].strip()
                            document_bytes = base64.b64decode(
                                normalized, validate=False)
                            if document_bytes:
                                document_id = hashlib.sha256(
                                    document_bytes).hexdigest()[:32]
                                self._document_store[document_id] = document_bytes
                                link_host = "localhost" if Config.HOST in (
                                    "0.0.0.0", "127.0.0.1") else Config.HOST
                                document_link = f"http://{link_host}:{Config.PORT}/documents/{document_id}"
                        except Exception:
                            document_link = ""

                processed_case = {
                    "case_number": case.get("caseNumber") or "",
                    "case_stage": case.get("caseStageName") or "",
                    "filing_date": case.get("caseFilingDate") or "",
                    "complainant": case.get("complainantName") or "",
                    "complainant_advocate": case.get("complainantAdvocateName") or "",
                    "respondent": case.get("respondentName") or "",
                    "respondent_advocate": case.get("respondentAdvocateName") or "",
                    "document_link": document_link
                }
                processed_cases.append(processed_case)

            logger.info(
                f"Successfully parsed {len(processed_cases)} cases from E-Jagriti API")
            return {"status": "success", "cases": processed_cases}

        except Exception as e:
            logger.error(f"Error parsing E-Jagriti API response: {str(e)}")
            return {"status": "error", "cases": []}

    # Removed unused HTML parsing logic as API uses JSON endpoints exclusively

    async def _fetch_real_states(self) -> List[StateResponse]:
        """Fetch real state data from Jagriti portal API"""
        try:
            # Use the real Jagriti API endpoint for states/commissions
            api_url = "https://e-jagriti.gov.in/services/report/report/getStateCommissionAndCircuitBench"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://e-jagriti.gov.in/"
            }

            response = await self.client.get(api_url, headers=headers)
            if response.status_code != 200:
                logger.warning(
                    f"API request failed with status {response.status_code}")
                return []

            # Parse JSON response
            data = response.json()
            if data.get('error') != 'false' or data.get('status') != 200:
                logger.warning(
                    f"API returned error: {data.get('message', 'Unknown error')}")
                return []

            states = []
            seen_states = set()

            # Process the data to extract unique states (excluding circuit benches for states list)
            for item in data.get('data', []):
                if not item.get('activeStatus', False):
                    continue

                commission_name = item.get(
                    'commissionNameEn', '').strip().upper()
                commission_id = str(item.get('commissionId', ''))
                is_circuit_bench = item.get(
                    'circuitAdditionBenchStatus', False)

                # For states list, we want main states, not circuit benches
                if not is_circuit_bench and commission_name and commission_id:
                    if commission_name not in seen_states:
                        states.append(StateResponse(
                            state_id=commission_id,
                            state_name=commission_name
                        ))
                        seen_states.add(commission_name)

            logger.info(f"Fetched {len(states)} real states from Jagriti API")
            return states

        except Exception as e:
            logger.error(f"Error fetching real states from API: {str(e)}")
            return []

    async def _fetch_real_commissions(self, state_id: str) -> List[CommissionResponse]:
        """Fetch real commission data for a state from Jagriti portal API"""
        try:
            # Use the real Jagriti API endpoint for district commissions
            api_url = "https://e-jagriti.gov.in/services/report/report/getDistrictCommissionByCommissionId"
            params = {"commissionId": state_id}

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://e-jagriti.gov.in/"
            }

            response = await self.client.get(api_url, params=params, headers=headers)

            if response.status_code != 200:
                logger.error(
                    f"Failed to fetch commissions for state {state_id}: HTTP {response.status_code}")
                return []

            data = response.json()

            if data.get('error') != 'false' or data.get('status') != 200:
                logger.error(
                    f"API error for state {state_id}: {data.get('message', 'Unknown error')}")
                return []

            commissions = []
            commission_data = data.get('data', [])

            logger.info(
                f"Fetched {len(commission_data)} commissions for state {state_id}")

            for item in commission_data:
                if item.get('activeStatus', False):  # Only include active commissions
                    commissions.append(CommissionResponse(
                        commission_id=str(item.get('commissionId', '')),
                        commission_name=item.get('commissionNameEn', ''),
                        state_id=state_id
                    ))

            return commissions

        except Exception as e:
            logger.error(f"Error fetching real commissions from API: {str(e)}")
            return []

    def _parse_cases(self, api_response: Dict) -> List[CaseResponse]:
        """Parse API response into CaseResponse objects"""
        cases = []

        if api_response.get("status") != "success":
            return cases

        for case_data in api_response.get("cases", []):
            case = CaseResponse(
                case_number=clean_text(case_data.get("case_number", "")),
                case_stage=clean_text(case_data.get("case_stage", "")),
                filing_date=case_data.get("filing_date", ""),
                complainant=clean_text(case_data.get("complainant", "")),
                complainant_advocate=clean_text(
                    case_data.get("complainant_advocate", "")),
                respondent=clean_text(case_data.get("respondent", "")),
                respondent_advocate=clean_text(
                    case_data.get("respondent_advocate", "")),
                document_link=case_data.get("document_link", "")
            )
            cases.append(case)

        return cases

    async def search_cases(self, request: CaseSearchRequest, search_type: SearchType) -> List[CaseResponse]:
        """Search cases using the specified search type"""

        # Use provided state and commission IDs directly
        state_id = request.state_id
        commission_id = request.commission_id

        # Set default date range if not provided
        if not request.from_date or not request.to_date:
            start_date, end_date = get_default_date_range()
            from_date = request.from_date or start_date
            to_date = request.to_date or end_date
        else:
            from_date = request.from_date
            to_date = request.to_date

        # Map search type to numeric serchType value (1-7)
        search_type_mapping = {
            SearchType.CASE_NUMBER: 1,
            SearchType.COMPLAINANT: 2,
            SearchType.RESPONDENT: 3,
            SearchType.COMPLAINANT_ADVOCATE: 4,
            SearchType.RESPONDENT_ADVOCATE: 5,
            SearchType.INDUSTRY_TYPE: 6,
            SearchType.JUDGE: 7
        }

        # Create payload for E-Jagriti API using the exact structure from response.json
        payload = JagritiSearchPayload(
            commissionId=int(commission_id),
            fromDate=format_date_for_jagriti(from_date),
            toDate=format_date_for_jagriti(to_date),
            serchType=search_type_mapping[search_type],
            serchTypeValue=request.search_value
        )

        # Make API request
        api_response = await self._make_jagriti_request(payload)

        # Parse and return cases
        return self._parse_cases(api_response)

    async def close(self):
        """Clean up resources"""
        await self.client.aclose()

    def get_document_bytes(self, document_id: str) -> Optional[bytes]:
        """Return stored document bytes for the given ID, if available"""
        return self._document_store.get(document_id)
