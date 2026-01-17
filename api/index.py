from flask import Flask, render_template, request, jsonify
from sympy import symbols, limit, diff, oo, latex
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)

x = symbols('x')

transformations = standard_transformations + (
    implicit_multiplication_application,
)

@app.route("/")
@app.route("/limit", methods=["GET"])
def func_limit():
    return render_template("limit.html")


@app.route("/derivative", methods=["GET", "POST"])
def func_derivative():
    result = None
    error = None
    function = ""

    if request.method == "POST":
        function = request.form.get("function", "")
        try:
            func = parse_expr(function, transformations=transformations)
            deriv = diff(func, x)
            result = latex(deriv)
        except Exception as e:
            error = str(e)

    return render_template(
        "derivative.html",
        result=result,
        error=error,
        function=function
    )
    
@app.route("/api/limit-preview", methods=["POST"])
def limit_preview():
    data = request.get_json()
    expr = data.get("function", "")
    x_value = data.get("x_value", "oo")

    try:
        func = parse_expr(expr, transformations=transformations)

        if x_value.lower() in ["oo", "inf", "infinity"]:
            x_latex = r"\infty"
        elif x_value.lower() in ["-oo", "-inf"]:
            x_latex = r"-\infty"
        else:
            x_latex = latex(parse_expr(x_value))

        return jsonify({
            "latex": rf"\lim_{{x \to {x_latex}}} {latex(func)}"
        })
    except Exception as e:
        return jsonify({"latex": ""})
    
@app.route("/api/derivative-preview", methods=["POST"])
def derivative_preview():
    data = request.get_json()
    expr = data.get("function", "")

    try:
        func = parse_expr(expr, transformations=transformations)
        return jsonify({
            "latex": latex(func)
        })
    except:
        return jsonify({"latex": ""})
    
def explain_limit(expr, x_val):
    steps = {}

    steps["function_latex"] = latex(expr)
    steps["x_value_latex"] = latex(x_val)

    substituted = expr.subs(x, x_val)
    steps["substituted_latex"] = latex(substituted)

    expr_str = latex(expr)
    x_val_str = latex(x_val)
    
    substituted_expr = expr_str.replace('x', f'({x_val_str})')
    
    steps["limit_latex"] = rf"\lim_{{x \to {x_val_str}}} {substituted_expr}"

    result = limit(expr, x, x_val)
    steps["result_latex"] = latex(result)

    return steps, result

@app.route("/api/limit-calc", methods=["POST"])
def limit_calc_api():
    function = request.form.get("function", "")
    x_value = request.form.get("x_value", "")

    try:
        func = parse_expr(function, transformations=transformations)

        if x_value.lower() in ["oo", "inf", "infinity"]:
            x_val = oo
        elif x_value.lower() in ["-oo", "-inf"]:
            x_val = -oo
        else:
            x_val = parse_expr(x_value, transformations=transformations)

        steps, result = explain_limit(func, x_val)

        return jsonify({
            "steps": steps,
            "result_latex": latex(result)
        })
    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route("/api/derivative-calc", methods=["POST"])
def derivative_calc_api():
    function = request.form.get("function", "")

    try:
        func = parse_expr(function, transformations=transformations)

        deriv = diff(func, x)

        return jsonify({
            "result_latex": latex(deriv)
        })
    except Exception as e:
        return jsonify({"error": str(e)})