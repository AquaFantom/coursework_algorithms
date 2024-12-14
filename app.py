import flet as ft
from genetic_alg import *
from initial import *


def create_row(schedule):
    row = []
    cells = []
    for trip in schedule.trips:
        cells.append(ft.DataCell(ft.Text(trip[0])))
        cells.append(ft.DataCell(ft.Text(trip[1])))
        for driver in schedule.schedule:
            if trip in schedule.schedule[driver]:
                cells.append(ft.DataCell(ft.Text(driver)))
                break
        row.append(ft.DataRow(cells=cells))
        cells = []
    return row


def create_tabs(week):
    tabs = []
    for schedule in week:
        tab = ft.Tab(
            text=f'{DAYS.get(schedule.day)}',
            content=ft.Column([
                ft.Text("Прибыль за день: " + str(schedule.fitness), size=20, text_align=ft.TextAlign.START),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Время отправления")),
                        ft.DataColumn(ft.Text("Время прибытия")),
                        ft.DataColumn(ft.Text("Водитель"))
                    ],
                    rows=create_row(schedule),
                    vertical_lines=ft.BorderSide(2),
                    horizontal_lines=ft.BorderSide(2),
                    ),
                ], scroll=ft.ScrollMode.ALWAYS, expand=1
            )
        )
        tabs.append(tab)
    return tabs


def create_driver_row(driver):
    row = []
    cells = []
    for day in driver.trips:
        for trip in driver.trips[day]:
            cells.append(ft.DataCell(ft.Text(DAYS.get(day))))
            cells.append(ft.DataCell(ft.Text(trip[0])))
            cells.append(ft.DataCell(ft.Text(trip[1])))
            row.append(ft.DataRow(cells=cells))
            cells = []
    return row


def create_drivers_tabs(week):
    tabs = []
    drivers = set()
    for day in week:
        for driver in day.drivers_a:
            drivers.add(driver)
        for driver in day.drivers_b:
            drivers.add(driver)
    for driver in drivers:
        tab = ft.Tab(
            text=f'{driver}',
            content=ft.Column([
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("День")),
                        ft.DataColumn(ft.Text("Время отправления")),
                        ft.DataColumn(ft.Text("Время прибытия")),
                    ],
                    rows=create_driver_row(driver),
                    vertical_lines=ft.BorderSide(2),
                    horizontal_lines=ft.BorderSide(2),
                ),
                ],
            scroll=ft.ScrollMode.ALWAYS, expand=1, alignment=ft.MainAxisAlignment.START
            )
        )
        tabs.append(tab)
    return tabs


def create_gui(week):
    MAIN_GUI = ft.Container(
        margin=ft.margin.only(bottom=10),
        expand=True,
        content=ft.Row([
            ft.Tabs(
                selected_index=0,
                animation_duration=300,
                expand=3,
                tabs=[
                    ft.Tab(
                        text="Расписание поездок",
                        icon=ft.icons.TABLE_VIEW,
                        content=ft.Container(
                            content=ft.Row([
                                ft.Tabs(
                                    tabs=create_tabs(week),
                                    expand=3,
                                ),
                            ]),
                            bgcolor=ft.colors.WHITE24,
                            padding=10,
                        )
                    ),
                    ft.Tab(
                        text="Расписание водителей",
                        icon=ft.icons.MANAGE_ACCOUNTS,
                        content=ft.Container(
                            content=ft.Row([
                                ft.Tabs(
                                    tabs=create_drivers_tabs(week),
                                    expand=3,
                                )
                            ]),
                            bgcolor=ft.colors.WHITE24,
                            padding=10,
                        )
                    )
                ],
            ), ft.Text("Прибыль за неделю: " + str(count_weekly_profit(week)), size=20, text_align=ft.TextAlign.START),
        ])
    )

    return MAIN_GUI


def main(page: ft.Page):
    page.padding = 20
    week = gen_algorithm(200)
    page.add(create_gui(week))
    page.update()


if __name__ == '__main__':
    ft.app(target=main)