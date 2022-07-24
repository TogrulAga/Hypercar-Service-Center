from collections import deque
import copy
from enum import Enum

from django.views import View
from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect


line_of_cars = {"change_oil": deque(), "inflate_tires": deque(), "diagnostic": deque()}
n_tickets = 0
ticket_number = 0


class Ticket(Enum):
    change_oil = 2
    inflate_tires = 5
    diagnostic = 30


class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "tickets/welcome.html")


class MenuView(TemplateView):
    template_name = "tickets/menu.html"


class TicketView(View):
    def get(self, request, ticket_type, *args, **kwargs):
        global line_of_cars, n_tickets
        n_tickets += 1
        line_of_cars[ticket_type].append(n_tickets)
        ticket_number = n_tickets

        estimated_time = self.get_estimated_time(line_of_cars, ticket_number, ticket_type)

        context = {"ticket_number": ticket_number, "estimated_time": estimated_time}

        return render(request, "tickets/ticket.html", context=context)

    @staticmethod
    def get_estimated_time(_line_of_cars, ticket_number, ticket_type):
        ticket_queue = copy.deepcopy(_line_of_cars)
        estimated_time = 0
        for ticket, q in ticket_queue.items():
            for number in q:
                if ticket == ticket_type and ticket_number == number:
                    return estimated_time
                estimated_time += Ticket[ticket].value
        return estimated_time


class RedirectView(View):
    url = ""

    def get(self, request, *args, **kwargs):
        return redirect(self.url)


class ProcessingView(View):
    def get(self, request, *args, **kwargs):
        n_change_oil = len(line_of_cars["change_oil"])
        n_inflate_tires = len(line_of_cars["inflate_tires"])
        n_diagnostic = len(line_of_cars["diagnostic"])

        context = {"n_change_oil": n_change_oil, "n_inflate_tires": n_inflate_tires, "n_diagnostic": n_diagnostic}

        return render(request, "tickets/processing.html", context=context)

    def post(self, request, *args, **kwargs):
        global line_of_cars, n_tickets, ticket_number

        ticket_number = 0
        if len(line_of_cars["change_oil"]) > 0:
            ticket_number = line_of_cars["change_oil"].popleft()
        elif len(line_of_cars["inflate_tires"]) > 0:
            ticket_number = line_of_cars["inflate_tires"].popleft()
        elif len(line_of_cars["diagnostic"]) > 0:
            ticket_number = line_of_cars["diagnostic"].popleft()

        if ticket_number != 0:
            n_tickets -= 1

        return redirect("/next")


class MonitorView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "tickets/monitor.html", context={"ticket_number": ticket_number})
