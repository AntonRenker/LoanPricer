import QuantLib as ql
import pandas as pd

class Schedule(pd.DataFrame):
    def cast_input(input: dict):
        # input.endOfMonthRule()
        # for dayCountConvention make switch case
        calendar_mapping = {
            "GER": ql.Germany(ql.Germany.Settlement),
            "UK": ql.UnitedKingdom(ql.UnitedKingdom.Settlement),
            "USA": ql.UnitedStates(ql.UnitedStates.Settlement),
            "AUS": ql.Australia(ql.Australia.Settlement),
            "BRA": ql.Brazil(ql.Brazil.Settlement),
            "CAN": ql.Canada(ql.Canada.Settlement),
            "SK": ql.SouthKorea(ql.SouthKorea.Settlement),
            "FRA": ql.France(ql.France.Settlement),
            "ITA": ql.Italy(ql.Italy.Settlement),
        }

        holidayConvention_mapping = {
            "cP": ql.Preceding,
            "cF": ql.Following,
            "cMF": ql.ModifiedFollowing,
            "cMP": ql.ModifiedPreceding,
            "cU": ql.Unadjusted,
            "cN": ql.NullCalendar(),
        }

        terminationDateConvention = {
            "tP": ql.Preceding,
            "tF": ql.Following,
            "tMF": ql.ModifiedFollowing,
            "tMP": ql.ModifiedPreceding,
            "tU": ql.Unadjusted,
            "tN": ql.NullCalendar(),
        }
        
        dateGenerationRule_mapping = {
            "dForward": ql.DateGeneration.Forward,
            "dBackward": ql.DateGeneration.Backward,
            "dZero": ql.DateGeneration.Zero,
            "dThirdWednesday": ql.DateGeneration.ThirdWednesday,
            "dTwentieth": ql.DateGeneration.Twentieth,
            "dTwentiethIMM": ql.DateGeneration.TwentiethIMM,
            "dOldCDS": ql.DateGeneration.OldCDS,
            "dCDS": ql.DateGeneration.CDS,
        }

        dayCountConvention_mapping = {
            "dcActual360": ql.Actual360(),
            "dcActual365Fixed": ql.Actual365Fixed(),
            "dcActualActualISDA": ql.ActualActual(ql.ActualActual.ISDA),
            "dcActualActualAFB": ql.ActualActual(ql.ActualActual.AFB),
            "dcActualActualISMA": ql.ActualActual(ql.ActualActual.ISMA),
            "dcBusiness252": ql.Business252(),
        }
        casted_input = {}

        casted_input["effectiveDate"] = ql.Date(input["effectiveDate"], "%Y-%m-%d")
        casted_input["tenor"] = input["tenor"]
        casted_input["frequency"] = ql.Period(input["frequency"])
        casted_input["calendar"] = calendar_mapping.get(input["calendar"], None)
        casted_input["holidayConvention"] = holidayConvention_mapping.get(input["holidayConvention"], None)
        casted_input["terminationDateConvention"] = terminationDateConvention.get(input["terminationDateConvention"], None)
        casted_input["dateGenerationRule"] = dateGenerationRule_mapping.get(input["dateGenerationRule"], None)
        casted_input["endOfMonthRule"] = input["endOfMonthRule"]
        casted_input["dayCountConvention"] = dayCountConvention_mapping.get(input["dayCountConvention"], None)

        return casted_input
    @staticmethod
    def init_with_ql(input: dict):
        input = Schedule.cast_input(input)
        effectiveDate = input.get("effectiveDate")
        tenorYears = int(input.get("tenor").split("Y")[0])
        #TODO catch 29th Feb
        terminationDate = ql.Date(effectiveDate.dayOfMonth(), effectiveDate.month(), effectiveDate.year() + tenorYears)
        ql_schedule = ql.Schedule(effectiveDate, terminationDate, input.get("frequency"), input.get("calendar"), input.get("holidayConvention"), input.get("terminationDateConvention"), input.get("dateGenerationRule"), input.get("endOfMonthRule"))

        schedule = Schedule(
            {
                "StartDate": list(ql_schedule)[:-1],
                "EndDate": list(ql_schedule)[1:],
            }
        )

        schedule["MidDate"] = [ql.Date((StartDate.serialNumber() + EndDate.serialNumber()) // 2) for StartDate, EndDate in zip(schedule.StartDate, schedule.EndDate)]

        schedule["DayCountFraction"] = [input.get("dayCountConvention").yearFraction(StartDate, EndDate) for StartDate, EndDate in zip(schedule.StartDate, schedule.EndDate)]
        schedule["DayCountFractionActAct"] = [ql.ActualActual(ql.ActualActual.ISDA).yearFraction(StartDate, EndDate) for StartDate, EndDate in zip(schedule.StartDate, schedule.EndDate)]

        return schedule