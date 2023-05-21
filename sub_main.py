import json, math
from enum import Enum


class VariableType(Enum):
    P = 0
    M = 1
    C = 2
    T = 3


class VariableInfo(Enum):
    N_READS = 0
    N_WRITES = 1
    IS_IN_CONDITION = 2
    IS_DECLARED = 3
    COUNT = 4
    IS_INIT = 5


def get_variable_type(variable_info, variable_name, prompted_variable_names):
    if not variable_info[VariableInfo.IS_DECLARED]:
        return None
    if not variable_info[VariableInfo.N_READS]:
        return VariableType.T
    if variable_info[VariableInfo.IS_IN_CONDITION]:
        return VariableType.C
    if variable_info[VariableInfo.N_WRITES] == 1 and variable_name in prompted_variable_names:
        return VariableType.P

    return VariableType.M


def get_program_info(text):
    import esprima

    variables = {}
    io_variable_names = set()
    prompted_variable_names = set()

    is_in_alert = False

    def go_in_alert():
        nonlocal is_in_alert
        is_in_alert = True

    def go_out_alert():
        nonlocal is_in_alert
        is_in_alert = False

    def process_variable(identifier, is_writed=False, is_in_condition=False, is_declaration=False, is_inited=False,
                         is_read=True):
        if not identifier in variables:
            variables[identifier] = {
                VariableInfo.N_READS: 0,
                VariableInfo.N_WRITES: 0,
                VariableInfo.IS_IN_CONDITION: False,
                VariableInfo.COUNT: 1,
                VariableInfo.IS_DECLARED: is_declaration
            }

            if is_inited:
                variables[identifier][VariableInfo.N_WRITES] += 1
            return

        if is_read:
            variables[identifier][VariableInfo.N_READS] += 1
        if is_writed:
            variables[identifier][VariableInfo.N_WRITES] += 1

        variables[identifier][VariableInfo.COUNT] += 1
        variables[identifier][VariableInfo.IS_IN_CONDITION] = variables[identifier][
                                                                  VariableInfo.IS_IN_CONDITION] or is_in_condition

        nonlocal is_in_alert
        if is_in_alert:
            io_variable_names.add(identifier)

    def parse_program(part, is_writed=False, is_in_condition=False):
        for block in part.body:
            check_part(block, is_writed, is_in_condition)

    def parse_variable_declaration(part, is_writed=False, is_in_condition=False):
        for item in part.declarations:
            check_part(item, is_writed, is_in_condition)

    def parse_variable_declarator(part, is_writed=False, is_in_condition=False):
        check_part(part.id, is_writed, is_in_condition, is_declaration=True, is_inited=part.init != None)
        if part.init != None:
            if part.init.type == "CallExpression" and part.init.callee.name == "prompt":
                io_variable_names.add(part.id.name)
                prompted_variable_names.add(part.id.name)
            check_part(part.init, is_writed, is_in_condition)

    def parse_call_expr(part, is_writed=False, is_in_condition=False):
        # check_part(part.callee, is_writed, is_in_condition)
        if part.callee.name == "alert":
            go_in_alert()
        for arg in part.arguments:
            check_part(arg, is_writed, is_in_condition)
        if part.callee.name == "alert":
            go_out_alert()

    def parse_identifier(part, is_writed=False, is_in_condition=False, is_declaration=False, is_inited=False,
                         is_read=True):
        process_variable(part.name, is_writed, is_in_condition, is_declaration, is_inited, is_read)

    def parse_literal(part, is_writed=False, is_in_condition=False):
        pass

    def parse_assignment_expr(part, is_writed=False, is_in_condition=False):
        check_part(part.left, True, is_in_condition, is_read=False)
        if (part.left.type == "Identifier" and part.right.type == "CallExpression" and
                part.right.callee.name == "prompt"):
            io_variable_names.add(part.left.name)
            prompted_variable_names.add(part.left.name)
        check_part(part.right, is_writed, is_in_condition)

    def parse_binary_expr(part, is_writed=False, is_in_condition=False):
        check_part(part.left, is_writed, is_in_condition)
        check_part(part.right, is_writed, is_in_condition)

    def parse_expr_statement(part, is_writed=False, is_in_condition=False):
        check_part(part.expression, is_writed, is_in_condition)

    def parse_if_statement(part, is_writed=False, is_in_condition=False):
        check_part(part.test, is_writed, is_in_condition=True)
        if part.alternate != None:
            check_part(part.alternate, is_writed, is_in_condition)
        else:
            pass
        check_part(part.consequent, is_writed, is_in_condition)

    def parse_block_statement(part, is_writed=False, is_in_condition=False):
        for item in part.body:
            check_part(item, is_writed, is_in_condition)

    def parse_for_statement(part, is_writed=False, is_in_condition=False):
        check_part(part.init, is_writed, is_in_condition)
        check_part(part.test, is_writed, is_in_condition=True)
        check_part(part.update, is_writed, is_in_condition)
        check_part(part.body, is_writed, is_in_condition)

    def parse_update_expr(part, is_writed=False, is_in_condition=False):
        check_part(part.argument, True, is_in_condition, is_read=False)

    def parse_while_statement(part, is_writed=False, is_in_condition=False):
        check_part(part.test, is_writed, is_in_condition=True)
        check_part(part.body, is_writed, is_in_condition)

    def parse_do_while_statement(part, is_writed=False, is_in_condition=False):
        check_part(part.body, is_writed, is_in_condition)
        check_part(part.test, is_writed, is_in_condition=True)

    def parse_func_declaration(part, is_writed=False, is_in_condition=False):
        for param in part.params:
            check_part(param, is_writed, is_in_condition)

        check_part(part.body, is_writed, is_in_condition)

    def parse_ret_statement(part, is_writed=False, is_in_condition=False):
        check_part(part.argument, is_writed, is_in_condition)

    def parse_switch_statement(part, is_writed=False, is_in_condition=False):
        check_part(part.discriminant, is_writed, True)
        for case_part in part.cases:
            check_part(case_part, is_writed, is_in_condition)

    def parse_switch_case(part, is_writed=False, is_in_condition=False):
        if part.test != None:
            check_part(part.test, is_writed, is_in_condition=True)
        for item in part.consequent:
            check_part(item, is_writed, is_in_condition)

    def parse_break_statement(part, is_writed=False, is_in_condition=False):
        pass

    def parse_continue_statement(part, is_writed=False, is_in_condition=False):
        pass

    def parse_unary_expr(part, is_writed=False, is_in_condition=False):
        check_part(part.argument, is_writed, is_in_condition)

    def parse_cond_expression(part, is_writed=False, is_in_condition=False):
        check_part(part.test, is_writed, is_in_condition=True)
        check_part(part.consequent, is_writed, is_in_condition)
        check_part(part.alternate, is_writed, is_in_condition)

    def parse_logical_expression(part, is_writed=False, is_in_condition=False):
        check_part(part.left, is_writed, is_in_condition)
        check_part(part.right, is_writed, is_in_condition)

    def check_part(part, is_writed=False, is_in_condition=False, is_declaration=False, is_inited=False, is_read=True):
        match part.type:
            case "Program":
                parse_program(part, is_writed, is_in_condition)

            case "VariableDeclaration":
                parse_variable_declaration(part, is_writed, is_in_condition)

            case "VariableDeclarator":
                parse_variable_declarator(part, is_writed, is_in_condition)

            case "CallExpression":
                parse_call_expr(part, is_writed, is_in_condition)

            case "Identifier":
                parse_identifier(part, is_writed, is_in_condition, is_declaration, is_inited, is_read)

            case "Literal":
                parse_literal(part, is_writed, is_in_condition)

            case "AssignmentExpression":
                parse_assignment_expr(part, is_writed, is_in_condition)

            case "BinaryExpression":
                parse_binary_expr(part, is_writed, is_in_condition)

            case "ExpressionStatement":
                parse_expr_statement(part, is_writed, is_in_condition)

            case "IfStatement":
                parse_if_statement(part, is_writed, is_in_condition)

            case "BlockStatement":
                parse_block_statement(part, is_writed, is_in_condition)

            case "ForStatement":
                parse_for_statement(part, is_writed, is_in_condition)

            case "UpdateExpression":
                parse_update_expr(part, is_writed, is_in_condition)

            case "WhileStatement":
                parse_while_statement(part, is_writed, is_in_condition)

            case "DoWhileStatement":
                parse_do_while_statement(part, is_writed, is_in_condition)

            case "FunctionDeclaration":
                parse_func_declaration(part, is_writed, is_in_condition)

            case "ReturnStatement":
                parse_ret_statement(part, is_writed, is_in_condition)

            case "SwitchStatement":
                parse_switch_statement(part, is_writed, is_in_condition)

            case "SwitchCase":
                parse_switch_case(part, is_writed, is_in_condition)

            case "BreakStatement":
                parse_break_statement(part, is_writed, is_in_condition)

            case "ContinueStatement":
                parse_continue_statement(part, is_writed, is_in_condition)

            case "UnaryExpression":
                parse_unary_expr(part, is_writed, is_in_condition)

            case "ConditionalExpression":
                parse_cond_expression(part, is_writed, is_in_condition)

            case "LogicalExpression":
                parse_logical_expression(part, is_writed, is_in_condition)

            case "ArrayExpression":
                for element in part.elements:
                    check_part(element, is_writed, is_in_condition)

    string = text
    result = esprima.parseScript(string)
    check_part(result)
    spens_result = []
    chepins_result = {
        VariableType.P: set(),
        VariableType.M: set(),
        VariableType.C: set(),
        VariableType.T: set()
    }
    io_chepins_result = {
        VariableType.P: set(),
        VariableType.M: set(),
        VariableType.C: set(),
        VariableType.T: set()
    }

    for variable, info in variables.items():
        spens_result.append((variable, info[VariableInfo.COUNT] - 1))
        variable_type = get_variable_type(info, variable, prompted_variable_names)
        print(f"{variable} + {info[VariableInfo.N_WRITES]}")
        if variable_type != None:
            chepins_result[variable_type].add(variable)
            if variable in io_variable_names:
                io_chepins_result[variable_type].add(variable)

    print(spens_result)
    print(chepins_result)
    print(io_chepins_result)

    return (spens_result, chepins_result, io_chepins_result)


def get_chepin_values(variables):
    result = {VariableType.P: 0,
              VariableType.C: 0,
              VariableType.M: 0,
              VariableType.T: 0}


if __name__ == "__main__":
    with open("script.js") as f:
        string = f.read()

    spens_result, chepins_result, io_chepins_result = get_program_info(string)
    for key, value in io_chepins_result.items():
        print(key)
        for item in value:
            print("    " + item)