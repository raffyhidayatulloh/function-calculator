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

@app.route("/derivative", methods=["GET"])
def func_derivative():
    return render_template("derivative.html" )
    
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
    
@app.route("/composition", methods=["GET"])
def func_composition():
    return render_template("composition.html")

@app.route("/api/composition-preview", methods=["POST"])
def composition_preview():
    data = request.get_json()

    f_str = data.get("functionF", "")
    g_str = data.get("functionG", "")
    mode = data.get("mode", "fog")

    try:
        f_expr = parse_expr(f_str, transformations=transformations)
        g_expr = parse_expr(g_str, transformations=transformations)

        if mode == "fog":
            composed = f_expr.subs(x, g_expr)
            latex_expr = rf"f(g(x)) = {latex(composed)}"
        else:
            composed = g_expr.subs(x, f_expr)
            latex_expr = rf"g(f(x)) = {latex(composed)}"

        return jsonify({"latex": latex_expr})

    except Exception:
        return jsonify({"latex": ""})

@app.route("/api/composition-calc", methods=["POST"])
def composition_calc():
    f_str = request.form.get("functionF", "")
    g_str = request.form.get("functionG", "")
    mode = request.form.get("mode", "fog")
    x_val_str = request.form.get("x_value", "").strip()

    try:
        f_expr = parse_expr(f_str, transformations=transformations)
        g_expr = parse_expr(g_str, transformations=transformations)

        steps = []
        eval_steps = []

        if mode == "fog":
            steps.append(r"(f \circ g)(x)")
            steps.append(r"f(g(x))")
            steps.append(rf"f({latex(g_expr)})")

            substituted = f_expr.subs(x, g_expr)
            steps.append(latex(substituted))

            simplified = substituted.simplify()
            title = "(f \\circ g)(x)"
        else:
            steps.append(r"(g \circ f)(x)")
            steps.append(r"g(f(x))")
            steps.append(rf"g({latex(f_expr)})")

            substituted = g_expr.subs(x, f_expr)
            steps.append(latex(substituted))

            simplified = substituted.simplify()
            title = "(g \\circ f)(x)"

        if x_val_str:
            x_val = parse_expr(x_val_str, transformations=transformations)

            eval_steps.append(r"\text{Evaluate}")
            eval_steps.append(rf"x = {latex(x_val)}")

            eval_steps.append(r"\text{Substitution}")

            raw_latex = latex(simplified).replace("x", rf"\left({latex(x_val)}\right)")

            eval_steps.append(rf"{title.replace('(x)', f'({latex(x_val)})')} = {raw_latex}")
            
            evaluated = simplified.subs(x, x_val)

            eval_steps.append(rf"{title.replace('(x)', f'({latex(x_val)})')} = {latex(evaluated)}")

            eval_steps.append(r"\text{Result}")
            eval_steps.append(latex(evaluated))

        return jsonify({
            "steps": steps,
            "result_latex": latex(simplified),
            "title": title,
            "eval_steps": eval_steps
        })

    except Exception as e:
        return jsonify({"error": str(e)})
    