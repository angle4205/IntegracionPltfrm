const path = require("path");

module.exports = {
  entry: "./apps/authentication/static/js/auth.js", // Path to your auth.js file
  output: {
    filename: "bundle.js",
    path: path.resolve(__dirname, "apps/authentication/static/js"),
  },
  mode: "development",
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"],
      },
    ],
  },
  resolve: {
    extensions: [".js"],
  },
};