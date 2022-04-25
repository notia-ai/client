from notia.models import DatasetMeta
from rich.console import Console
from rich.table import Table
from rich import box
from typing import List, Optional


class Display:
    def __init__(self) -> None:
        self._console = Console()

    def log(self, msg_obj=None) -> None:
        self._console.print(msg_obj, style="bold green")

    def warning(self, msg_obj=None) -> None:
        self._console.print(msg_obj, style="bold yellow")

    def error(self, msg_obj=None) -> None:
        self._console.print(msg_obj, style="bold red")

    def log_styled(self, msg_obj=None, style: Optional[str] = None) -> None:
        self._console.print(msg_obj, style=style)

    def datasetsAsTable(self, datasets: List[DatasetMeta]) -> None:
        table = Table(show_header=True, expand=True, box=box.ROUNDED)
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Size", justify="right")
        for dataset in datasets:
            table.add_row(
                dataset.slug, dataset.name, self._displayFileSize(float(dataset.size))
            )

        self._console.print(table)

    def ordersAsTable(self, orders) -> None:
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Name")
        table.add_column("Size")
        for order in orders:
            table.add_row(order["purchase_name"], order["purchase_size"])
        self._console.print(table)

    def _displayFileSize(self, filesize: float, suffix="B") -> str:
        for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
            if abs(filesize) < 1024.0:
                return f"{filesize:3.1f}{unit}{suffix}"
            filesize /= 1024.0
        return f"{filesize:.1f}Yi{suffix}"
