import json
from dataclasses import dataclass
from typing import Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class FHIRResponse:
    status_code: int
    resource_type: str
    resource_id: str
    body: Dict


class FHIRClientError(Exception):
    pass


class FHIRClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8080/fhir",
        timeout: int = 10,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def create_resource(
        self,
        resource: Dict,
    ) -> FHIRResponse:
        resource_type = resource.get(
            "resourceType",
            "",
        )

        if not resource_type:
            raise FHIRClientError(
                "FHIR resourceType is required"
            )

        url = (
            f"{self.base_url}/"
            f"{resource_type}"
        )

        payload = json.dumps(
            resource
        ).encode("utf-8")

        request = Request(
            url=url,
            data=payload,
            method="POST",
            headers={
                "Content-Type": (
                    "application/fhir+json"
                ),
                "Accept": (
                    "application/fhir+json"
                ),
            },
        )

        try:
            with urlopen(
                request,
                timeout=self.timeout,
            ) as response:

                response_body = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )

                resource_id = (
                    response_body.get(
                        "id",
                        "",
                    )
                )

                if not resource_id:
                    raise FHIRClientError(
                        "FHIR server response "
                        "does not contain resource id"
                    )

                return FHIRResponse(
                    status_code=response.status,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    body=response_body,
                )

        except HTTPError as exc:
            body = exc.read().decode(
                "utf-8",
                errors="replace",
            )

            raise FHIRClientError(
                f"FHIR HTTP error "
                f"{exc.code}: {body}"
            ) from exc

        except URLError as exc:
            raise FHIRClientError(
                f"FHIR connection error: "
                f"{exc.reason}"
            ) from exc
