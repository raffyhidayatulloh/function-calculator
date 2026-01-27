from flask import Flask, render_template, request, jsonify
from sympy import symbols, limit, diff, oo, latex, factor, cancel
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
def index():
    return render_template("index.html")

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

    # Substituted
    substituted = expr.subs(x, x_val)
    steps["substituted_latex"] = latex(substituted)

    expr_str = latex(expr)
    x_val_str = latex(x_val)
    substituted_expr = expr_str.replace('x', f'({x_val_str})')
    steps["limit_latex"] = rf"\lim_{{x \to {x_val_str}}} {substituted_expr}"

    factoring = None
    simplified_limit = None
    simplified_evaluation = None
    indeterminate = None
    
    # Indeterminate form
    try:
        num, den = expr.as_numer_denom()
        num_sub = num.subs(x, x_val)
        den_sub = den.subs(x, x_val)

        #  0/0
        if num_sub == 0 and den_sub == 0:
            indeterminate = r"\frac{0}{0}"
            
            num_fact = factor(num)
            den_fact = factor(den)

            factoring = rf"\frac{{{latex(num_fact)}}}{{{latex(den_fact)}}}"

            simplified_expr = cancel(expr)
            simplified_limit = rf"\lim_{{x \to {x_val_str}}} {latex(simplified_expr)}"
            
            simplified_expr_str = latex(simplified_expr)
            simplified_evaluation = rf"\lim_{{x \to {x_val_str}}} {simplified_expr_str.replace('x', f'({x_val_str})')}"

    except Exception:
        pass

    result = limit(expr, x, x_val)
    steps["indeterminate_latex"] = indeterminate
    steps["factoring_latex"] = factoring
    steps["simplified_limit_latex"] = simplified_limit
    steps["simplified_evaluation_latex"] = simplified_evaluation
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

@app.route("/api/composition-calc", methods=["POST"])
def composition_calc():
    f_str = request.form.get("functionF", "")
    g_str = request.form.get("functionG", "")
    mode = request.form.get("mode", "fog")
    x_val_str = request.form.get("x_value", "").strip()

    try:
        f_expr = parse_expr(f_str, transformations=transformations)
        g_expr = parse_expr(g_str, transformations=transformations)

        eval_steps = []

        if mode == "fog":
            substituted = f_expr.subs(x, g_expr)
            simplified = substituted.simplify()
            title = "(f \\circ g)(x)"
        else:
            substituted = g_expr.subs(x, f_expr)
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
            "result_latex": latex(simplified),
            "title": title,
            "eval_steps": eval_steps
        })

    except Exception as e:
        return jsonify({"error": str(e)})
    