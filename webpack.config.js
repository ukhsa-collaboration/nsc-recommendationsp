const webpack = require('webpack');
const path = require('path');
const CleanWebpackPlugin = require('clean-webpack-plugin').CleanWebpackPlugin;
const CopyPlugin = require('copy-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

const devServerPort = 8080;
const pathRoot = 'frontend';
const pathDist = `${pathRoot}/dist`;
const pathDistGov = path.resolve(__dirname, pathDist, 'govuk');

const config = {
  entry: {
    'index': `./${pathRoot}/src/index.js`,
    'style': `./${pathRoot}/src/index.scss`
  },
  output: {
    path: path.resolve(__dirname, pathDist),
    publicPath: '/frontend/dist/',
    filename: '[name].js',
    library: "NSCR"
  },
  devtool: 'source-map',
  devServer: {
    static: {
      directory: path.resolve(__dirname, pathDist),
      publicPath: '/frontend/dist/',
    },
    hot: true,
    allowedHosts: 'all',
    port: devServerPort,
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
    devMiddleware: {
      publicPath: '/frontend/dist/', 
      writeToDisk: (filePath) => {
        return filePath.startsWith(pathDistGov);
      },
    },
  },
  resolve: {
    extensions: ['.js', '.json'],
  },
  plugins: [
    new CleanWebpackPlugin({
      cleanOnceBeforeBuildPatterns: ['**/*', '!.gitkeep'],
    }),
    new MiniCssExtractPlugin({
      filename: '[name].css',
    }),
    new CopyPlugin({
      patterns: [
        {
          context: path.resolve(__dirname, 'node_modules', 'govuk-frontend', 'dist', 'govuk', 'assets'),
          from: '**/*',
          to: pathDistGov,
        },
      ],
    }),
  ],
  module: {
    rules: [
      {
        test: /\.js$/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
          },
        },
      },
      {
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: 'css-loader',
            options: {
              url: false,
            }
          },
          {
            loader: 'resolve-url-loader',
            options: {
              sourceMap: true,
              disable: false,
            },
          },
          {
            loader: 'sass-loader',
            options: {
              sassOptions: {
                includePaths: ['./node_modules'],
                sourceMap: true,
                quietDeps: true,
                sourceMapContents: false,
              },
              sourceMap: true,
            },
          },
        ],
      },
    ],
  },
  optimization: {
    minimize: true,
    minimizer: [
      new CssMinimizerPlugin(),
    ],
  },
};

module.exports = (env, argv) => {
  if (argv.mode === 'production') {
    console.log('Running in production mode');
  } else {
    console.log('Running in development mode');
  }
  return config;
};
