from flask import Flask, render_template, request
from sympy import symbols, sympify, limit, diff, latex, oo
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)

app = Flask(__name__)
x = symbols('x')


@app.route("/")
def home():
    return render_template("limit.html")


@app.route("/limit", methods=["GET", "POST"])
def func_limit():
    result = None
    error = None
    function = ""
    x_value = ""

    transformations = standard_transformations + (
        implicit_multiplication_application,
    )

    if request.method == "POST":
        function = request.form.get("function", "")
        x_value = request.form.get("x_value", "")

        try:
            func = parse_expr(function, transformations=transformations)

            # support oo / infinity
            if x_value.lower() in ["oo", "inf", "infinity"]:
                x_val = oo
            elif x_value.lower() in ["-oo", "-inf"]:
                x_val = -oo
            else:
                x_val = parse_expr(x_value, transformations=transformations)

            result = limit(func, x, x_val)

        except Exception as e:
            error = str(e)

    return render_template(
        "limit.html",
        result=result,
        error=error,
        function=function,
        x_value=x_value
    )


@app.route("/derivative", methods=["GET", "POST"])
def func_derivative():
    result = None
    error = None
    function = ""

    transformations = standard_transformations + (
        implicit_multiplication_application,
    )

    if request.method == "POST":
        function = request.form["function"]
        try:
            func = parse_expr(function, transformations=transformations)
            result = diff(func, x)
        except Exception as e:
            error = str(e)

    return render_template(
        "derivative.html",
        result=result,
        error=error,
        function=function
    )


if __name__ == "__main__":
    app.run(debug=True)
