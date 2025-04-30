const CleanWebpackPlugin = require('clean-webpack-plugin').CleanWebpackPlugin;
const CopyPlugin = require('copy-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin'); // Updated import
const path = require('path');
const setPublicPath = require('@microsoft/set-webpack-public-path-plugin');
const webpack = require('webpack');

// Only embed assets under 10 KB
const embedLimit = 10 * 1024;

const devServerPort = 8080;

const pathRoot = 'frontend';
const pathDist = `${pathRoot}/dist`;
const pathDistGov = path.resolve(__dirname, pathDist, 'govuk');

/*
** Rules which change depending on mode
*/

// Image optimisation rule
const moduleRuleOptimiseImages = {
  test: /\.(gif|png|jpe?g|svg)$/i,
  loader: 'image-webpack-loader',
  options: {
    // Apply the loader before url-loader and svg-url-loader
    enforce: 'pre',
    // Disabled in dev, enable in production
    disable: true,
  },
};

// Style building rule
const moduleRuleScss = {// Style building rule
    test: /\.scss$/,
    use: [
      'style-loader',
      'css-loader',
      {
        loader: 'resolve-url-loader',
        options: {
          'sourceMap': true,
          disable: false
        },
      },
      {
        loader: 'sass-loader',
        options: {
          sassOptions: {
            includePaths: ['./node_modules'],  // Make sure this is included
            sourceMap: true,
            quietDeps: true,     
            sourceMapContents: false
          },
          sourceMap: true,
        },
      },
    ],
  };
  

/*
** Main config
*/
const config = {
  entry: {
    'index': `./${pathRoot}/src/index.js`,
    'style': `./${pathRoot}/src/index.scss`
  },
  output: {
    path: path.resolve(__dirname, pathDist),
    publicPath: `/${pathDist}/`,
    filename: '[name].js',
    library: "NSCR"
  },

  devtool: 'source-map',
  devServer: {
    devMiddleware: {
      writeToDisk: (filePath) => {
        return filePath.startsWith(pathDistGov);
      },
    },
    contentBase: path.resolve(__dirname, pathDist),
    contentBasePublicPath: '/static/',
    publicPath: '/static/',
    hot: true,
    disableHostCheck: true,
    port: devServerPort,
    headers: {
      'Access-Control-Allow-Origin': '*'
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
          context: path.resolve(
            __dirname,
            'node_modules',
            'govuk-frontend',
            'dist',
            'govuk',
            'assets'
          ),
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

      moduleRuleOptimiseImages,

      {
        test: /\.(png|jpg|gif|eot|ttf|woff|woff2)$/,
        loader: 'url-loader',
        options: {
          limit: embedLimit,
        },
      },
      {
        test: /\.svg$/,
        loader: 'svg-url-loader',
        options: {
          limit: embedLimit,
          noquotes: true,
        }
      },

      moduleRuleScss,
    ],
  },

  optimization: {
    minimize: true,
    minimizer: [
      new CssMinimizerPlugin(), // Minifies CSS
    ],
  },
};

module.exports = (env, argv) => {
  if (argv.mode === 'production') {
    console.log(`Running in production mode:
* optimising images
* extracting and minifying CSS
    `);

    moduleRuleScss.use[0] = MiniCssExtractPlugin.loader;
    moduleRuleOptimiseImages.options.disable = false;
    config.plugins.push(new CssMinimizerPlugin());  // Add minifier for CSS
  } else if (process.argv[1].indexOf('webpack-dev-server') !== -1) {
    console.log('Running in development mode with HMR');
    config.plugins.push(
      new webpack.HotModuleReplacementPlugin(),
      new setPublicPath.SetPublicPathPlugin({
        scriptName: {
          name: '[name]\.js',
          isTokenized: true,
        },
      }),
    );
  } else {
    console.log('Running in development mode');
    config.plugins.push(
      new webpack.HotModuleReplacementPlugin(),
    )
  }
  return config;
}
